# Chapter 12 · Production Operations Discipline

## The problem

In a personal project, development and operations are the same person. Once you give the agent ssh and database access, it can do as much as you can: query production data, change production data, deploy, restart services.

Most of the time this is convenient. When something goes wrong, it often can't be undone: bad data written with no snapshot, a restart during the business peak that loses data still being collected, a command carrying a password ending up in the logs.

## The idea

- **Reads and writes take two separate paths, each with its own entry point.** Querying data is fine at any time, and it is done with a read-only account; changing data goes through a dedicated process.
- **Every write to production data goes through the write process** (the "writing production data goes through a dedicated process" item among Chapter 5's risk add-ons refers to exactly this). A write requires the confirmation phrase, and the phrase is valid only for the version of the plan that was laid out; "OK" or "go ahead and run it" don't count.
- **Deployment has a single entry point, with the gates written into the script.** No hotfix method of any kind may be used to get around it.
- **By default, production is left alone during the business peak.** Writing data has no exceptions; a deploy that crosses the peak window needs the human's explicit consent, with the cost of doing it this time written down. The window value has a single source of truth, read live, never copied.
- **Credentials never appear in the conversation, command-line arguments, logs, or commits.**
- **Automated actions must be registered, and kept few.** What may be restarted automatically and what may not is written down in advance.
- **Post-release verification is kept as a dated checklist**, with automatic reminders when items fall due, instead of relying on memory.

## In practice

### Read-only queries: two channels

We recommend that both channels use a **read-only role**; they differ only in how much they can read:

| Channel | Who uses it | Recommended restrictions |
|---|---|---|
| Main-session channel | You and the main session | Read-only role that can read all business tables; writes go only through the write process below |
| Reviewer read-only channel | Review subagents, command-line review (Chapter 7) | A read-only role with fewer privileges; sensitive tables (accounts, payments, users' private content) are not granted; on the server side, this account is restricted to running one fixed query entry point |

To be frank, in the author's project the main-session channel currently uses a business account that can write, and "read, never write" is held in place by rules alone. As Chapter 2 says, written rules are not enforcement, so the practice recommended here is stricter than where the author's project stands today.

**A minimal read-only setup.** The read-only role (the syntax of the SQL below was tested inside a transaction on a local PostgreSQL 18):

```sql
CREATE ROLE ro_reader LOGIN;                                  -- password set separately, never in the script
ALTER ROLE ro_reader SET default_transaction_read_only = on;  -- read-only transactions by default
ALTER ROLE ro_reader SET statement_timeout = '15s';           -- keep big queries from dragging production down
GRANT CONNECT ON DATABASE <db_name> TO ro_reader;
GRANT USAGE ON SCHEMA public TO ro_reader;
GRANT SELECT ON <readable_table>, <readable_table> TO ro_reader;  -- grant only the tables to be read; never sensitive ones
```

`default_transaction_read_only` is only a default and can be changed within a session; what actually blocks writes is that "only `SELECT` was granted".

Wrap a query entry point around it, for example a script that:

- reads one SQL statement from standard input, accepts only statements starting with `SELECT`, `WITH`, or `EXPLAIN`, one at a time;
- connects with the read-only role to run it, with a timeout;
- for the reviewer's account, is bound to it with an ssh forced command (the `command=` option in `authorized_keys`), so that after logging in that account can run only this entry point.

The `/db-readonly` skill in the examples in Chapters 3 and 7 is what teaches the agent to call this entry point: when to query, one query at a time, and attaching the query statement and time to the results.

A few habits for how to write it:

- **Write the SQL into a temporary file, upload it, then run it.** Nesting quotes on an ssh command line, plus Chinese column names, means stepping on several layers of escaping.
- **Passwords stay out of command-line arguments and connection URLs.** Use a password file (PostgreSQL's `.pgpass`, with permissions set to 600), or a temporary environment variable set only for that one command. Command-line arguments show up in the process list and the shell history; more insidious is **exception concatenation on failure**: when a command fails, the subprocess libraries of some languages splice the entire command line (plaintext password included) into the error, which then goes out with the tool output.
- **The local side is more dangerous.** Database connection variables inherited by the shell may be pointing at a tunnel to production. In that case, what you think is a "local trial run" is a real run on production. Before acting, confirm which database is actually in effect.

### Writing production data: authorization plus six steps

**Authorization (step 0).** First lay the plan out for the human: the script or SQL, the write scope (which table, what conditions), the estimated number of affected rows, the snapshot table name, the rollback method, and the planned execution time. Execute only after the human replies with the agreed confirmation phrase (for example, "confirm plan"). For any other wording, ask again. If any item in the plan changes, lay it out again and ask for the phrase again. A confirmation phrase for a deploy is not authorization to write to the database.

**1. A full trial run on a non-production database.** Record the output and how long it took. A trial run only proves "the script runs end to end", not "the result on production is right"; the latter is what steps 2 and 5 are for.

**2. Measure the impact read-only, and write the rollback.**

- Count two sets of numbers: the rows **currently** within the write scope (step 3 checks the snapshot against this), and the estimated number of affected rows (steps 4 and 5 check the actuals against this). Count the first and last boundary days separately as well.
- Check for leftovers: a snapshot table with the same name, half-finished output from a previously interrupted run. If you find any, stop and report first.
- List the other writers that write the same tables (scheduled jobs, collection processes), and pick an execution time that avoids them.
- List the snapshot tables derived from these tables: when the source table changes, derived tables don't follow on their own. For each one, write down "recompute or not, and why".
- Avoid the business peak.
- **Write the rollback SQL before executing, and dry-run it once on a non-production database.**

The rollback works as "delete the whole range, then write the snapshot back as whole rows", which suits inserts, updates, and upserts alike. Expected deleted rows = snapshot rows + rows added by the write − rows deleted by the write, written as a literal. Don't use a live count taken with the same WHERE as the expectation: counts from the same source are bound to be equal, and can't catch a wrong scope.

```sql
-- rollback.sql: no BEGIN / COMMIT here; the transaction is supplied from outside
DO $$
DECLARE n_del bigint; n_ins bigint; n_snap bigint;
  n_del_expect constant bigint := <expected_deleted_rows>;
BEGIN
  SELECT count(*) INTO n_snap FROM <table>_bak_<date>;
  DELETE FROM <table> WHERE <same_scope_condition_as_the_snapshot>;
  GET DIAGNOSTICS n_del = ROW_COUNT;
  IF n_del <> n_del_expect THEN
    RAISE EXCEPTION 'deleted % rows, expected % rows, rolling back everything', n_del, n_del_expect;
  END IF;
  INSERT INTO <table> SELECT * FROM <table>_bak_<date>;
  GET DIAGNOSTICS n_ins = ROW_COUNT;
  IF n_ins <> n_snap THEN
    RAISE EXCEPTION 'wrote back % rows, snapshot has % rows, rolling back everything', n_ins, n_snap;
  END IF;
END $$;
```

Before copying it, confirm three things: no other table references this one with a foreign key (otherwise the range delete will cascade or be blocked); since the snapshot, no columns have been added or dropped and the column order hasn't changed (`INSERT … SELECT *` matches by position, so a changed column order can silently write values into the wrong columns); and since the write, no other writer has touched this range (the range delete would wipe out what they wrote as well).

**The dry run** uses a separate `drill.sql`, with **each command on its own line**:

```sql
BEGIN;
\ir write.sql
SELECT …;            -- look at the effect after the write
\ir rollback.sql
SELECT …;            -- check that the rollback restored the original state
ROLLBACK;
```

Run it with `psql -v ON_ERROR_STOP=1 -f drill.sql`. Three notes:

- psql meta-commands such as `\ir` treat everything after them on the same line as their arguments. If you write it on one line (`BEGIN; \ir rollback.sql; SELECT …; ROLLBACK;`), the queries after it and the `ROLLBACK` are **silently ignored**, with only a few lines of warnings (tested on psql 18).
- Files pulled in by `\ir` must not contain `BEGIN` / `COMMIT`; otherwise the `COMMIT` inside them will still commit.
- This template was tested locally on a temporary table: the data changed after the write, was restored after the rollback, and the run aborted with an error when the expected row count was wrong.

**3. Snapshot.**

- `CREATE TABLE <table>_bak_<date> AS SELECT * FROM <table> WHERE <same_scope_condition_as_the_write>;`
- **Take all columns; don't pick columns**: columns you leave out can't be rolled back.
- The snapshot and the write use **the same WHERE**. But the same WHERE only guarantees that the two agree, not that the WHERE itself is right, so after creating the snapshot, query its minimum date, maximum date, the row counts for the first and last days, and the total row count, and check each against the numbers from step 2. If anything doesn't match, stop.
- Write date conditions as date literals; don't compare against timezone-aware timestamp parameters (see "Pitfalls we hit" below).
- The nightly full-database backup can't replace it: a full restore would also roll back everything written afterwards (inference, not rehearsed).

**4. Execute.**

- **Backfill and recompute scripts in the codebase**: what runs on production must be the version **already deployed**; never copy a separately modified script up and run it.
- **One-off hand-written SQL files**: these may be uploaded and run, but their content must be exactly the version laid out in step 0 (you can attach the file hash so the human can check it).
- Save the full output to disk: the reconciliation numbers appear only this once.
- For hand-written SQL, write the expected row count into the SQL itself, inside a `DO` block:

  ```sql
  DO $$
  DECLARE n bigint;
  BEGIN
    UPDATE <table> SET … WHERE <scope_condition>;
    GET DIAGNOSTICS n = ROW_COUNT;
    IF n <> <estimated_rows> THEN
      RAISE EXCEPTION 'expected <estimated_rows> rows, got % rows', n;
    END IF;
  END $$;
  ```

  Run it with `psql -v ON_ERROR_STOP=1 --single-transaction -f write.sql`: any mismatch raises an error and the whole file rolls back. (For the **real run**, `--single-transaction` is exactly what you want: commit only if everything succeeds. It can't be used for a dry run; see "Pitfalls we hit" below.)

**5. Reconciliation.**

- Compare before and after: row counts, the distribution of changes, business invariants. If it doesn't match the estimate, stop: don't rerun, don't delete the snapshot, and report the discrepancy to the human.
- **Take at least one recomputation path that is independent of the script itself.** The script's built-in reconciliation shares the same scope condition as the write, and agreement from the same source is not evidence (Chapter 11).

**6. Wrap-up.** Keep the snapshot until the human has confirmed the reconciliation results, then delete it by its exact table name and confirm nothing is left behind. In the Log section of the corresponding spec, record the execution time, the command, the reconciliation numbers, the snapshot table name, and when it was deleted.

This doesn't apply to schema changes: changes to table structure go through database migrations and ship with a deploy.

### Deployment: a single entry point

- **Only one deploy script can ship to production**, with the gates written into the script's first step (Chapter 2). In the author's project the gates include: tests pass, a clean working tree, explicit confirmation from the human, and not during the business peak. They're listed here only for illustration; in your project the script is authoritative (Chapter 4). If a gate fails, the script exits without ever touching the server.
- **No getting around the script**: syncing build output straight to the server, ssh-ing in to pull code and restart, or building on the spot on a small-memory server are all forbidden. If you find someone doing this, stop and flag it.
- **The confirmation phrase includes the test mode.** In one sentence the human gives both the "confirm" and "where the tests run", so the agent doesn't need to ask further:
  
  | Phrase | Meaning |
  |---|---|
  | "Confirm deploy, test locally" (default) | Actually run the equivalent tests locally, then deploy |
  | "Confirm deploy, via CI" | Trigger CI on the remote first, wait for a successful result, then deploy |
  | "Confirm deploy, skip tests" | Skip the test gate; all other gates are still checked |
  
  Saying only "confirm deploy" uses the default mode. "Not via CI" is ambiguous: treat it as testing locally and say so; never escalate it to skipping tests on your own.
- **A confirmation is valid only for the current commit.** If the code changes after confirmation, confirm again.
- **What the script's confirmation flag buys is visibility and friction, not proof of authorization.** The agent is perfectly able to add the "confirmed" flag itself. The only way to have the machine enforce "the human confirmed" is a mechanism like `ask` that the human must click personally (Chapter 10's token gate works this way), and even that only guards against carelessness. Don't take a passed gate to mean you've been authorized.
- **No deploys during the business peak window by default.** The window value lives only in the deploy check script, read live, never copied (Chapter 4). If you really must deploy during the peak (an urgent fix, say), the human explicitly agrees and the cost is written down at the same time: which data being collected will be lost to this restart. The script keeps a separate override flag for this, and you must ask the human before using it.

### Automated actions: few, and registered

The conventions in the author's project:

- Across the whole pipeline, exactly one script is allowed to restart the application process automatically (when memory exceeds its limit);
- **The database is never restarted automatically**;
- Automated health checks and alert triage produce only text, and have no authority to execute anything;
- Any new automated action is first registered in the allowlist in the deployment runbook (Chapter 8), and only then goes live.

### Sensitive data

- Never echo the contents of files like `.env` into the conversation. When you need to refer to configuration, give only the key name, never the value.
- Database passwords, secrets, and server private keys are never written into code, commit messages, or logs.
- If you find hard-coded credentials in the repo, **tell the human first; don't automatically "fix" them into environment variables**: the credentials may already have leaked and need rotating first, and quietly changing them only hides the problem.

### Production verification to-dos

Many post-release verifications can only be done at a particular time: after the next day's market close, over three consecutive trading days, at the end of some month. Keep them as a list:

- Each item states **the earliest day and time of day** it can be verified, what to verify, and the criterion.
- A session-start hook reads this list and reports "how many items are due, and how many days overdue the oldest one is", prompting you to decide whether to deal with them now.
- For items whose data can be fetched automatically, a scheduled fetch script on the server pulls the data when the time comes and leaves evidence behind; **the judgment is still made by the agent**: it checks that the time window, the preconditions, and the criterion line up, then writes the conclusion into the list and ticks the item off. The first time a given check is judged this way, the agent writes a separate **independent query** and fetches again: agreement from the same source can't prove the fetch's definition is right.

## Costs and when it applies

- The write process is heavy. Every write to production data has to go through it: authorization, snapshot, and reconciliation can never be skipped; for small, reversible data fixes, the checklist in step 2 can be trimmed to fit the situation.
- The read-only channel, the confirmation phrases, and the gate scripts all have to be set up first. When starting out, do at least three things: query production with a read-only account, take a snapshot before changing production, and deploy through one script only.
- "Business peak" should be defined by your business: big sales events for e-commerce, class hours for education, trading hours in the author's project.

## Pitfalls we hit

### Deploying at peak time: two days of data permanently lost

Some kinds of data are sampled in real time by the application process during business hours and then written, and the raw data they depend on is kept only briefly. Deploying during business hours two days in a row meant the restarts cut off the sampling; that data is permanently missing and can't be rebuilt after the fact.

**Fix**: the deploy check script gained a "business peak window" gate, with the window value living only in the script; crossing it requires the human's explicit consent, with the cost written down.

### We thought we were rehearsing the rollback; it actually committed

To prepare for a production write, we dry-ran the rollback SQL beforehand against the local database, using `psql --single-transaction -f rollback.sql` in the belief that "it rolls back when it finishes". In fact `--single-transaction` only wraps the whole file in a single `BEGIN … COMMIT`, so when it finishes it still **commits**. As luck would have it, the rollback SQL also had no expected deleted row count; and the negative test run beforehand to prove the guardrail could catch mistakes had its direction reversed, so the guardrail wasn't actually working. The result: nearly 130,000 rows of existing data in a local table were deleted, plus over 5,000 rows of trial-run data (production was unaffected).

**Fix**: always dry-run with the line-by-line `drill.sql` above, wrapped in `BEGIN … ROLLBACK`; hard-code the expected deleted row count into the rollback SQL, and raise an exception if it doesn't match.

### The snapshot took only a few columns, and the WHERE missed a day

In one data fix, the snapshot picked only 7 columns, so on rollback the other columns (such as the algorithm version and the computation time) couldn't be restored. In the same fix, the date condition shared by the snapshot and the script's reconciliation left out the start day in both: the database session's time zone was UTC+8 (Beijing time), so `DATE '2026-09-08' >= TIMESTAMPTZ '2026-09-08 00:00:00+00'` was false, and the whole start day was excluded. The two sides agreed, so neither caught it; in the end it was an independent recomputation that found it.

**Fix**: snapshot all columns; write date conditions as date literals; after creating the snapshot, check the minimum and maximum dates and the first- and last-day row counts one by one.

### Having the user call a production API from their own terminal got their IP banned

Production has automatic banning: requests sent by scripts are treated as crawlers. The agent's own request was blocked by a local hook, and the hook's message said "please have the user run this in their own terminal", so the agent asked the user to call a production API once from their terminal. The user's terminal and the agent go out through the same network egress, so the IP was banned immediately and had to be unbanned by hand.

**Fix**:

- When you need to make an anonymous request to a production API, make it from the server itself, not through the public network egress; automated browser access to production follows the exemption method the project specifies.
- A hook's block message must not steer the human into running the blocked request from their local terminal: that just hands the same risk over to the human.

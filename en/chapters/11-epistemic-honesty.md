# Chapter 11 · Epistemic Honesty

## The problem

The most dangerous mistake an AI coding agent makes isn't writing wrong code; it's **confidently giving a conclusion that looks well-reasoned but has no basis**.

Hand it a batch of untrustworthy data and it will produce an interpretation; challenge it, and it will write a more rigorous analysis; challenge it again, and it will write an "honest document" or even a "deep retrospective". Each step looks more convincing, and the error never changes. A well-reasoned-looking substitute is far more dangerous than "I don't know": you're most likely to take it at face value on exactly the occasion that matters.

## The idea

**When there's no trustworthy basis, the correct output is no output.**

Say precisely "I don't know" or "I can't verify X", and then stop. Don't fill that gap with analysis, documents, checklists, or even reflection that makes it look substantial.

This is written as an **always-on at session start** rule (Chapter 3) that every session carries. Here are its parts.

### Five signals that lead the agent astray

Stop as soon as you recognize one:

1. **Looking for an explanation of a conclusion, instead of first reporting the contradiction.** This includes when tool output and instructions don't match. Explanation is the entry point for fabrication: first say plainly "this doesn't match", and don't absorb it into a self-consistent narrative.
2. **The result is unusually clean, confirms the hypothesis exactly, or is exactly the answer the other side wants.** This is when to be more alert, not to relax. Real data usually has rough edges.
3. **Searching again for a definite conclusion that will hold up.** When the data collapses, look for a stratification; when the stratification collapses, look for a case-cracking story... This urge to "find somewhere to land" is itself a signal. Allow yourself to stay in uncertainty.
4. **An explanation that casts you as the clear-headed victim or the detective**, rather than the one who made the mistake ("the system is lying to me"). The more flattering the explanation, the more suspect it is; prefer the simpler one that gives you less credit.
5. **The confidence shown exceeds the actual evidence.** Match your tone to the strength of the evidence; don't use declarative sentences for things you haven't verified.

### Every factual claim must be able to answer

- **What's the source**: tool output, your own inference, or a guess? Tag it directly where it matters. The "Pitfalls we hit" section of Chapter 10 uses these tags, for example [owner's words] [inference].
- **Can it be independently cross-checked**: use several logically independent paths and see whether they converge. **If all the paths share a source** (they all come from the same untrustworthy channel, or are all self-generated), **convergence is not evidence**.
- **Separate three layers**, without fudging and without giving up:
  
  | Layer | How to handle it |
  |---|---|
  | What can be cross-checked | Pin it down, and state the basis |
  | What conflicts with each other | Call it a contradiction, and state both sides |
  | What truly can't be found | Leave it blank; don't invent a cause |
  
  "Nothing can be determined" is laziness too.

### Code logic from local, data facts from production

**Investigating "how the code runs" can be done reading only local; investigating "what the data looks like" must take production as the authority.**

The local database isn't a scaled-down copy of the production database; it's a different database: tables may be empty, values may be stale, and production's messy data shapes may not exist at all. A conclusion drawn from it isn't "not precise enough"; it's a conclusion about a different object.

The test, in one sentence: **does this conclusion involve "how many rows, what values, whether this kind of data exists"? If so, you must check production.** Checking production goes through the read-only channel (Chapter 12).

On the semantics of external data, comments in the code and code written from those comments share a source and can't vouch for each other; the only independent path is to check the data itself.

### Sources that can't serve as evidence of the current state

- PRDs, specs, proposals: they record what was planned at the time, not what is now (Chapter 8).
- Past review reports, incident records: snapshots, history.
- Auto-generated code graphs: auxiliary only. Don't use the graph and the spec as evidence for each other: if the graph ingested the spec and the spec cites the graph, that's circular self-confirmation.

## In practice

### A sample always-on rule

Put a rule like the following into the always-on rules at session start (Chapter 3); about ten lines is enough:

```markdown
# Epistemic honesty

When there's no trustworthy basis, the correct output is no output: say "I don't know / can't verify X", then stop.

- Stop on these signals: looking for an explanation of a conclusion instead of reporting the contradiction; a result that's unusually clean; rushing to find a conclusion that holds up;
  an explanation that casts you as victim or detective; a tone stronger than the evidence.
- Tag the source of every claim that matters: [tool output] [inference] [guess]. When all paths share a source, convergence doesn't count as evidence.
- Write conclusions in three layers: what can be cross-checked / what conflicts with each other / what truly can't be found. Leave the unfindable blank; don't invent a cause.
- If a conclusion involves "how many rows, what values, whether this kind of data exists", check production (read-only channel); don't use the local database as evidence.
- PRDs, specs, past reports, and generated graphs are not evidence of the current state.
```

### A sample report

Below is a fictional investigation conclusion, demonstrating the three layers and the source tags:

```markdown
## Conclusion: yesterday's daily report is missing 3 channels

**What can be cross-checked**
- The daily report table has only 9 channels for yesterday ([tool output] production read-only query, 2026-11-10 14:05, SQL attached);
  the collection log also has success records for only 9 channels that day ([tool output] server log). The two paths are independent and agree.

**What conflicts with each other**
- The channel config table has 12 enabled, but the collection job's startup log loaded only 9. The cause hasn't been located yet; no guessing.

**What truly can't be found**
- Whether the upstream for those 3 channels produced data that day: there are no upstream access records, so it can't be found.

**Not read, not verified**
- Didn't read the collection job's retry logic; "gives up after three retries" is an [inference] from the function name.
```

### A few everyday habits

- Attach the query itself and the time it was run to any data conclusion, so others can re-run it.
- End a report with a separate section, "Verified and unverified assumptions" or "Not read, not verified". Chapter 7's design review template requires reviewers to write this; in this book's own reviews, the reviewers' reports all ended with this section too.
- Admit what you can't confirm from the inside: whether a step was actually executed, whether a piece of output was generated by you. Say so proactively when it's relevant; don't wait to be asked.

## Costs and when it applies

- "I don't know" makes a conversation feel less smooth, and users sometimes press: "then take a guess". Guessing is fine, but label it clearly as a guess.
- Checking production requires a safe read-only channel. If you don't have one, build the channel first rather than making do with local (Chapter 12).
- This guideline is a written rule and depends on the model complying (Chapter 2). The parts that can be written as check items (for example, "data conclusions must include the query") can go into the review checklist; the rest relies on the human's follow-up questions.

## Pitfalls we hit

### Untrustworthy data wrapped, step by step, into a conclusion, a document, a retrospective

This is where the guideline came from. After getting a batch of untrustworthy data, the agent wrote, in sequence, "an interpretation → a case-cracking narrative → an honest document → a deep retrospective", each step repeating the same mistake in a more sophisticated form, until questioning layer by layer finally made it clear.

The basis for this one is that conversation itself, not any tool output. The guideline constrains "how the agent acts"; it makes no claims about facts in the outside world.

### Three times in one day, the local database taken as evidence for data

| # | What the agent said | Reality | Why it was wrong | Which discipline it maps to |
|---|---|---|---|---|
| 1 | "The migration hasn't been applied locally yet" | It had long been applied | What it read was a database connection pointing elsewhere, not the local database | First confirm which database is actually in effect (Chapter 12) |
| 2 | "We need to rerun the script to backfill that batch of dirty values" | Most had long since been recomputed; only a few rows were left | Inferred only from the migration's semantics, without checking the current state in production | Data conclusions must be checked against production |
| 3 | "This table has 0 rows locally, so we need a conservative fallback when no baseline is available" | Production had tens of thousands of rows | Took the empty table as the norm and designed an entire degradation path around it | Code from local, data from production |

What the three have in common: each gave a data conclusion without checking the right database, or without checking at all.

No. 3 is the one most worth remembering: **an empty local table leads the agent to design for "can't determine" as the main scenario**, when production has plenty of data. The same change also built a wrong conversion formula: its premise came from a code comment, and the second path used to "confirm" it was also written from that comment. This is a textbook case of "convergence of paths sharing a source is not evidence".

### Explaining an anomaly is easier than reporting it

After a format checker was fixed, running it on existing files produced a large number of failures. At the time, two kinds of cases were spot-checked, and the matter was closed as "it's all legacy formatting, not the script misjudging".

That conclusion was itself a misjudgment. Reproducing them one by one showed that several kinds were defects in the script itself: of the 57 reds in one re-run, 24 were pure false positives. Worse, closing it that way trained a habit of "a red lint doesn't matter".

**The correct move is to verify the tool itself first, then attribute the existing failures.** This one is more worth remembering than "didn't verify": it was verifying halfway, then making up a story for the remaining anomalies.

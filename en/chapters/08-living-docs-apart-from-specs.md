# Chapter 8 · Keep Living Docs Apart from Specs

## The problem

After a while of spec-driven development, the repo fills up with documents: PRDs, specs, designs, task lists, proposals, post-mortems... When the agent has to answer "what does the system look like now," it naturally goes and reads these documents.

The trouble is that most of them describe **what we planned to do at the time**. The plan changed at launch, then another requirement changed it again later, and the documents never followed. The agent reads a spec from three months ago and confidently tells you the system "should" work that way.

Conversely, documents that really do describe the current state go stale within weeks if nobody maintains them, and a stale current-state document is worse than none.

## The idea

**Documents fall into three kinds, with different roles and different uses:**

| Kind | Answers | Examples | Can it be trusted as the current state? |
|---|---|---|---|
| **Living docs** | What it looks like now | Architecture overview, data model overview, deployment runbook, metric definitions table | Yes: it's maintained together with the code; when it conflicts with the authoritative source, the authoritative source wins |
| **Process docs** | What we planned to do at the time, and why it was decided that way | PRDs, specs, designs, task lists, proposals | No: it's a snapshot of one change |
| **Incident records** | Why a given rule exists | Each rule file has a matching incident record | No: it's history |

One more kind isn't in the table: **automatically generated artifacts** such as a code knowledge graph. For how to use them, see "Generated artifacts: check the date first" below.

One more principle: **the authoritative source comes first.** Living docs are only a guided tour. Table structure is defined by the schema file, scheduled jobs by the code that registers them, rules by the rule files. When a living doc conflicts with the authoritative source, trust the authoritative source and go back and fix the living doc.

## In practice

### The doc map: the agent's first map

Put a `docs/README.md` in the docs directory as the agent's entry point into the docs. Just having it there isn't enough; the agent has to know to read it first: add a line to the entry file's trigger table, "before answering questions about architecture or the current state → read `docs/README.md` first" (Chapter 3). The writing rules below are delivered through a path-scoped rule with `paths: docs/**`.

The map contains three things:

- A one-sentence principle: which docs are living docs, which aren't, and which to trust in a conflict;
- The directory structure: one line per living doc, saying what it covers;
- **An authoritative-source table**:
  
  | Topic | Authoritative source | Guided tour in the living docs |
  |---|---|---|
  | Database table structure | `schema` file | Data model overview |
  | Scheduled jobs | The code that registers the scheduled jobs | Scheduling timeline |
  | What a given change agreed to do (intent) | That change's spec. It doesn't answer "what does the system look like now"; once the change is done, look at the code and the living docs for the current state | — |
  | Code conventions, git workflow | Rule files and skills | — |
  | Deployment process | Deploy scripts and deploy rules | Deployment runbook |

- When adding a living doc, register it in the map at the same time, or nobody will find it. This can be held in place by a self-test: scan the docs directory and fail on any unregistered living doc (the same kind of self-test as the one guarding mappings in Chapter 4).

### Living docs describe only the current state

Living docs answer "what does it look like now"; all change history lives in git. So:

- **Corrections leave no trace.** When you find a sentence is wrong, just change it to the right one. Don't write "this line originally said X, corrected on such-and-such date." Traces mixed into the body make the reader wade through "what it used to wrongly say" in every section.
- **No revision history, last-updated date, "last verified on," or similar sections or footers.** They get updated only when someone remembers, so they are structurally bound to lag, and readers who judge freshness by them will reach the wrong conclusion.
- **Lessons worth keeping are written as present-tense warnings**: "Don't write it as X: that causes Y," "You can't judge by A: because B." Dated measurements stay as they are; that date marks when the measurement was taken, not when the doc was edited.
- **Removed features get no tombstone paragraphs.** At most one sentence, "doesn't exist; use X instead," to stop people following old notes.
- **Don't hard-code numbers that drift** (table counts, row counts, line numbers): write the name of the authoritative source plus a command to check live (Chapter 4).

The test in one sentence: **if you deleted this sentence, would the reader's understanding of "what it looks like now" get worse?** If not, it belongs in git log, not in a living doc.

### Code changes must sync the docs

Make a **doc sync table**: which kinds of code change must update which living doc **in the same commit**. For example:

| Code change | Living doc that must be synced |
|---|---|
| Change the database schema (add or drop tables, change a field's meaning) | Data model overview |
| Add or remove scheduled jobs | Scheduling timeline |
| Add a new app, switch tech stacks, major-version upgrade of a core dependency | Architecture overview |
| Change deployment, environment variables, CI config | The matching section of the deployment runbook |
| Change how a metric is calculated | Metric definitions table |

- **Why the same commit**: once a living doc falls behind the code, readers can only treat it as history, and it is no longer a living doc.
- **The test matters more than the table**: if a change would turn any existing statement in a living doc into a falsehood, sync it, whether or not it matches a row in the table word for word.
- **Pre-commit self-check**: treat this table as a pre-commit checklist; if a row applies, add the doc change in the same commit.
- **Machines can only remind, not judge.** A pre-commit hook can print a warning when "a certain kind of code is staged but the matching doc isn't"; but which sentence has become false is beyond what a machine can judge, so when you see the warning, actually go and look.
- Don't stuff one-off "development completion summaries," "test reports," or "deployment plans" into the living-docs area; those are process docs.

### Process docs: frozen once done

- A spec is frozen once its change is done; for how, see Chapter 5, "A spec is a change snapshot, not a living doc."
- A PRD is the source of intent, not of the current state; once it's turned into a spec, the spec is authoritative for the requirements (Chapter 6). New facts discovered while executing the spec are fed back into the PRD's confirmation items; when that spec is done, the PRD is archived along with it and not changed after that.
- Both can be committed and read, but when you read them, keep in mind: this is "what we planned at the time," not "what is now."

### Incident records: the "why" behind a rule

- Each rule file has a matching incident record with the same name. The rule body keeps only one line, "post-mortem: see such-and-such"; the story and the evidence live in the incident record.
- Append by date; once written, entries aren't changed, and the only thing allowed is appending a "Follow-up" at the end of an entry.
- It's history: read it only when following a pointer from a rule, and don't use it to judge the current state.

### Generated artifacts: check the date first

Automatically generated things such as a code knowledge graph can help you see cross-module relationships, but they have a generation time and won't tell you when they're out of date. Check the generation date before using one; check key conclusions against the source code or the living docs.

Also watch for circular self-confirmation: if the graph ingested the specs, and the specs in turn cite the graph, the two "corroborating each other" is not evidence (Chapter 11).

## Costs and when it applies

- Living docs have to change along with the code, which adds a few minutes to each commit. At the start, maintain only the two or three most frequently asked about (architecture, data model, deployment), and add more once "the agent got it wrong following an old description" happens.
- The doc sync table has to be tailored to each project. The table itself isn't what matters; what matters is the habit of asking, "I changed code, so which sentence in the docs has become false?"

## Pitfalls we hit

### PRDs weren't committed, which forced specs to copy whole sections of them

Early on, PRDs lived in a private directory that wasn't committed, so the agent couldn't read them. To make specs readable on their own, several specs had to copy the PRD's conclusions into the requirements file wholesale. So the same conclusion existed in two copies, exactly the kind Chapter 4 describes, bound to drift sooner or later.

**Fix**: PRDs are now committed and readable, but their role hasn't changed: still the source of intent, not the authority on the current state. Specs are rewritten from the PRD's decision digest, citing the source item by item, not copying whole sections (Chapter 6).

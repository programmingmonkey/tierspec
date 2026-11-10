# Chapter 5 · Tiering

## The problem

The most common complaint about spec-driven development is that it turns every change into a small waterfall: even fixing a typo means writing requirements first, then a design, then breaking it into tasks. That ends one of two ways: either the process gets seen as a nuisance and is gradually bypassed, or the human ends up following the agent around, producing piles of documents nobody reads.

Go the other way and write nothing at all, and you crash on the changes that really are complex: halfway through you discover the impact is bigger than you thought, or an irreversible step has already run.

## The idea

**How heavy the process is follows the change. First spend a little time on read-only investigation to see the change clearly, then decide how heavy a process to run.**

TierSpec decides the tier by asking two layers of questions, in order:

- **First, the three Tier C criteria**: Is there a step that can't be undone? Is there a trade-off the human will have to sign off on repeatedly? Does it need an audit trail? If any one holds, it's C: run the full process.
- **If none holds, ask two more questions**: Can the fix be stated in one sentence? Has the impact been verified? If the answers are "yes" and "yes, verified", it's A: change it directly. Otherwise it's B: write a lightweight plan.

The order matters: "drop a column" can be stated in one sentence, but it can't be undone, so it's C, not A.

Two more principles run through the whole chapter:

- **Risk doesn't set the tier, it only adds requirements.** A high-risk change doesn't necessarily get a heavier process, but it always gets extra requirements on top of its tier, and high risk counts on its own: "it's a tiny change" doesn't water it down.
- **The size of the change plays no part in tiering.** What's being judged is "does this need to be done in steps", not line count. A thousand-line mechanical rename can be A; a one-line definition change can be C.

## In practice

### Step 1: Classify the type

| Type | What changes | Verification discipline |
|---|---|---|
| Product requirement | Behavior the user can see is going to change | Verify the new behavior, and also verify that adjacent old behavior isn't broken |
| Technical rework | The product system, with user-visible behavior unchanged | **Prove the old behavior first**, then prove after the change that behavior hasn't changed |
| Bug fix | Behavior in the product system that was wrong to begin with | **Reproduce first**: write a test that fails on the old code, then fix |
| Engineering task | The development system: tools, rules, CI, scripts, agent config | Verify that the gate really blocks and really lets things through (negative control) |

Ask in order: Is it the development system that's changing? Was the original behavior wrong? Is user-visible behavior going to change? If a change touches two types, classify it by the main driver and write in the other type's requirements as a supplement.

### Step 2: Read-only investigation, then the four-line report

The investigation is read-only: no code changes, and no changes to files in the repo (temporary scripts for reproducing go outside the repo). Go deep enough to write the four lines below:

```
Root cause: … (for product requirements, technical rework and engineering tasks, write "Goal")
Impact: the list of callers and consumers, and how it was compiled
Similar cases: where else the same pattern or the same definition appears, how they were enumerated, and how each is handled (required for bug fixes)
Fix: if it can be stated in one sentence, write that sentence; if not, write where it's stuck
```

- When a conclusion involves "how many rows, what value, does this kind of data exist", check production, not the local database (Chapter 11).
- If this change will overturn behavior fixed in an old spec, an existing test or an earlier decision, say in the four lines which one it overturns, and wait for the human to nod. When it goes into the spec, mark each item "Added / Modified / Removed" and cite the matching acceptance-criterion number in the old spec.
- For things that don't change behavior, like fixing typos or copy, skip the investigation and change it directly.

### Step 3: Decide the tier

Judge the table **from the bottom up**: check C's three criteria first, and if any holds, it's C; otherwise choose between A and B.

| Tier | Criteria | Output |
|---|---|---|
| **A: change directly** | The fix can be stated in one sentence, **and** the impact has been verified during the investigation | No files; the four lines go in the commit message |
| **B: lightweight plan** | The fix can't be stated clearly, or the root cause or impact still needs investigating | A single `spec.md`: Goals and non-goals, Approach and steps, Log |
| **C: full process** | Any of: a step that can't be undone; a trade-off the human must sign off on repeatedly; an audit trail is needed | Three files: `requirements.md` → `design.md` → `tasks.md`; for product requirements, try to produce a PRD with a prototype first (Chapter 6) |

The bar for "can be stated in one sentence": one sentence can say where this diff changes things and how, **and it can be done in one commit and verified in one verification pass**. If it has to be done in several steps, each verified separately, it can't be stated in one sentence. Just listing which files to change doesn't count as stating it.

Examples of "can't be undone": dropping a column, dropping a table, changing a column's type on a large table; bulk production data writes without a snapshot; a definition that can't be taken back once published externally. A small-scope database write with a snapshot that can be rolled back doesn't count as irreversible; but whatever the tier and whatever the risk, every write to production data goes through the write procedure in Chapter 12.

**Who decides**: the agent recommends, the human decides. For A with low risk, the agent can go ahead right after the four-line report; everything else waits for the human. When recommending B, attach the draft right away, so a single reply both sets the tier and approves the plan.

### Step 4: Risk add-ons

| Risk | Includes | Requirements added on top of the tier |
|---|---|---|
| **Low** | Can be rolled back; mistakes show up immediately | None |
| **Medium** | Ordinary database migrations (adding a column, adding an index); changing a data or metric definition (how a number is calculated, which items a list picks, how it sorts); changing the gates and guardrails themselves (git hooks, CI, lint, deploy scripts, monitoring alerts, backups); background, scheduled and async pipelines; external data sources (onboarding, switching source, rate limiting, degradation); new dependencies or major-version dependency upgrades; gateways, certificates, domains | Even if it's A, report the recommendation first and wait for the human to say yes. For changes to gates and guardrails, verify by actually triggering them once (negative control); seeing the script run isn't enough |
| **High** | Permissions and authentication; payments and billing; privacy; silent failures that reach multiple consumers; migrations that hold locks on large tables or rewrite whole tables, migrations that require pausing writes | Everything required at Medium, plus: before starting, write three sentences, **fix, verification, rollback**, and only proceed once the human approves; for Tier A, copy those three sentences verbatim into the commit message; the production-data write step may not be trimmed (Chapter 12) |

The **must-ask list** is the Medium and High levels, plus "can't be undone" from the Tier C criteria: even if a change is small enough to look like A, report the recommendation first and wait for the human to say yes.

### The Tier A commit message

A writes no files; all the evidence lives in the commit message. The first line is a one-sentence title as usual, then a blank line, then the four lines:

```
<one-sentence title: what changed>

Root cause: … (or "Goal: …")
Impact: … (how it was compiled)
Similar cases: <command or scope>, <handling>          (required for bug fixes)
Fix: <one sentence>
Test: <test name>, fails before the fix, passes after  (required for bug fixes)
Evidence: read-only production query <date>, <result>  (when the conclusion involves data)
```

High-risk changes add two more lines, "Verification" and "Rollback". When there's no testable behavior (pure styling, pure copy), the "Test" line says "None: <reason>", and spells out how a human checks it by eye.

### Structure of Tiers B and C

First, the directory convention: each spec lives in a directory named after its topic; when one topic is split into several specs, the topic directory gets a "topic README" with the overall goal, the split table and the release order. Every spec opens with a status line whose values are "Draft → Approved → In progress → Done", plus "Shelved".

**B: one file, three sections.**

```
spec.md
  1 Goals and non-goals   the human's own words or a source, at least one non-goal ("what we won't do"), acceptance criteria (one verdict each; where there's a failure path, write the error path), definitions to verify and their sources, open questions
  2 Approach and steps    tasks, each with a "Verification"
  3 Log                   who decided what on which day, changes during execution
```

**C: three files; after each one, stop and wait for the human to review it.**

```
requirements.md   1 Background and goals · 2 Scope (including at least one non-goal) · 3 Acceptance criteria (numbered, each one can be judged right or wrong)
design.md         4 Current state and approach (each current-state item tagged with source and date; phasing table)
tasks.md          5 Tasks · 6 Log
```

- Write at least one non-goal, to draw the boundary for the implementer so the agent doesn't fill things in on its own.
- Once the requirements are written, the author does a self-check first: does each acceptance criterion have only one way to judge it? Then sweep the dimensions that are easy to miss: non-functional (performance, reliability, observability, security and privacy), what happens when an external dependency fails, whether terms are used consistently throughout, whether the done signal can be tested, and whether any placeholders or vague words are left.
- When the human says "go on to the next one", the previous file counts as passed. Ask for approval only once all three have passed; the approval is its own commit, and only then can work start.
- **Always write requirements first, not design first.** For product requirements, ambiguity has already been asked and settled round by round in the PRD's confirmation items (Chapter 6); technical Tier C work gets no separate "clarifying questions" stage: ambiguities are written as explicit assumptions, and the human's review is the backstop. In Tier B, anything uncertain goes into the open questions under "Goals and non-goals", each with a default approach.
- **Size and phasing**: past 20 executable tasks, stop and think; past 40, you must split into several specs. Slice vertically by "can ship independently, can be verified independently", not horizontally by "build the tables first, then the endpoints, then the tests". Every phase in the phasing table must state "can it ship independently", and be able to answer "who verifies it, and what do they verify".

### Mid-execution re-check

Tiering isn't a one-time thing. At three points, ask again against the original four lines: after the premises have been verified at the start of work; when tests turn up a counterexample, or a trial run doesn't match expectations; and every time a change is logged.

- Can the fix still be stated in one sentence? Is the impact still what the investigation found? Has a step that can't be undone appeared, or a trade-off the human must decide?
- If any answer has changed, stop, report to the human, and re-tier (if A turns out not to be statable in one sentence, switch to B).
- If the risk level changes, the tier doesn't necessarily change, but add the risk add-ons for the new level.

### Completion check

- Before claiming the work is done, the author re-runs verification against each acceptance criterion and attaches the results from this run, not a result from some run during development.
- When the human asks, dispatch a reviewer **that took no part in execution** to do the completion check: it reads only the requirements, the Log section and this spec's commits, and for each criterion gives evidence from re-running it on the current code. The conclusion can't be bigger than the evidence: whatever wasn't run gets written down as not run.
- During the completion check, the reviewer may run verification commands such as tests, type checks and builds; other commands that write or change state are still off limits (the reviewer definition in Chapter 7).

### A spec is a change snapshot, not a living doc

Once the work is done, the spec is frozen: problems found later are appended to the Log section, and the body isn't revised; changing behavior means opening a new spec. For "what the system looks like now", look at the code and the living docs (Chapter 8).

### A structure-only lint

The spec format is held in place by a small lint hooked into pre-commit: are task lines and numbering correctly formatted, is the status one of the valid values, is there a task section, does every task have a "Verification". **It checks structure only, not content**: whether the content is right depends on the author's self-check and the human's review.

## Costs and when it applies

- "Read-only investigation first" takes time, and on small changes it can feel redundant. But it's exactly this step that lands most changes in A: if after the investigation the fix can be stated in one sentence, no files need to be written.
- Tiering needs the human involved. If the human always replies "whatever you think", the tier degrades into the agent deciding on its own, and the "wait for the human to say yes" parts of the risk add-ons stop working.
- The tier criteria can be adjusted per project, but keep the structure of the two questions and "risk only adds requirements".

## Pitfalls we hit

### The spec rules themselves bloated until nobody could read them through

The old spec rules kept getting patched until they reached 37KB, too long to read in one go, and became a file that was "nominally binding, actually impossible to read end to end".

**Fix**: rewrote them as a lean version, about 7KB, that doesn't depend on any particular tool, so any agent reading plain markdown can follow it, paired with a small structure-only lint; the old rules were demoted to apply only to existing specs. To be frank, it slowly grew back with practice, and by 2026-11 it was about 69KB again. So one rewrite isn't enough: every time it grows, run it through Chapter 4's bar for adding and removing rules.

### The format lint failed silently four times

There was once a hook that checked spec task formatting, treated as the only enforcement backstop. It failed silently four separate times, each time with no signal at all. See "A guardrail existing ≠ a guardrail working" in Chapter 2.

**Fix**: the lint was replaced by a standalone script hooked into pre-commit, with its own self-test of positive cases, negative cases and a control group.

## Sources and comparisons

### How this maps to Claude Code's official best practices

Many of TierSpec's practices point in the same direction as the advice in Claude Code's official docs. The table below compares against three official doc pages as read in 2026-11: [Best practices](https://code.claude.com/docs/en/best-practices), [Memory](https://code.claude.com/docs/en/memory), [Common workflows](https://code.claude.com/docs/en/common-workflows). The left column is the official advice (in parentheses: "page name · original section name"); the right column is TierSpec's corresponding practice.

| Official advice | What TierSpec does | See |
|---|---|---|
| When you're not yet sure what you want, brainstorm with Claude first: have it interview you until a spec can be written, put it in SPEC.md, then start a new session to implement from it (Best practices · Brainstorm with Claude first) | For Tier C product requirements, produce a PRD first where possible: the human writes the skeleton, the agent completes it and lists the ambiguities as Pending items, answered round by round; once decided, it's turned into a spec and executed from the spec | Chapter 6 |
| Review the plan before changes hit disk; use plan mode (Common workflows · Plan before editing) | Before acting, do a read-only investigation and give the four-line report, and the human decides the tier (Tier A with low risk can go ahead right after the report); for Tiers B and C the plan is written to a file and executed only after approval | This chapter |
| Give Claude a check that produces "pass / fail", and make it show evidence: just saying "the tests all pass" proves nothing (Best practices · Give Claude a check to run) | Every task carries a "Verification"; on completion, re-run and attach this run's results; for bug fixes, first write a test that fails on the old code; data conclusions come with the query and when it was run | This chapter, Chapter 11 |
| Have a subagent review against the spec, report only gaps that affect correctness, and explicitly skip style issues (Best practices · Review against your spec) | Two independent reviews; the prompt asks for correctness issues and acceptance-criteria violations only, not style | Chapter 7 |
| Distinguish deterministic from non-deterministic instructions: things that must happen every time become a hook, a deny rule or a managed setting (Best practices · Deterministic and non-deterministic instructions) | Same direction, but TierSpec is more conservative: Claude hooks let things through when their checker errors out, and the model can edit them too, so they only count as an aid; what must hold goes into hard gates like git hooks, lint and tests, script gates and CI | Chapters 1, 2 |
| Keep CLAUDE.md short, aiming for under 200 lines per file (Memory · Write effective instructions); only write what Claude can't work out from reading the code (Best practices · Keep CLAUDE.md short, Tell Claude what it can't see) | The entry file is only a map; adding a rule means first clearing three bars: "not obvious, has actually gone wrong, written specifically" | Chapters 3, 4 |
| Scope local rules with `paths:`; put the team's multi-step procedures into skills (Best practices · Scope rules to one part of the codebase, Put team procedures in skills) | Path-scoped rules; multi-step procedures become skills | Chapters 1, 3 |
| If two corrections haven't fixed it, clear the context and write a better prompt instead of correcting a third time (Best practices · Steer the session) | Similar in spirit: the mid-execution re-check; when the fix can no longer be stated in one sentence, stop and re-tier instead of grinding on | This chapter |
| For a read-only review subagent, restrict its tools to Read, Grep, Glob, enforced by Claude Code (Best practices · Know what subagents cost) | The author's project gives its reviewers a shell, to look at git diff and query production data; the price is that "read-only" rests on convention; you can tighten this as the official docs suggest | Chapters 1, 7 |

TierSpec does a few things beyond the official advice:

- **Tiers.** For requirements that aren't thought through yet, the official docs suggest interviewing your way to a SPEC.md before implementing; TierSpec tiers every change first: Tier A writes no files, Tier B one, Tier C three (and for product requirements, a PRD where possible).
- **Risk add-ons.** Risk doesn't decide how much documentation to write, but it does decide whether to ask the human first and whether to write a rollback.
- **Evidence from production.** Data conclusions don't rest on the local database (Chapter 11).
- **Quantified review.** Use a sample set to compare hit counts before and after a change to the review process (Chapter 7).

The official docs get updated; when you use them, go by the current version you read.

### Trade-offs against other SDD methods

When the author's project rebuilt its spec system in 2026-09, it compared several open-source spec-driven development projects, including [GitHub Spec Kit](https://github.com/github/spec-kit), [OpenSpec](https://github.com/Fission-AI/OpenSpec), [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) and [cc-sdd](https://github.com/gotalab/cc-sdd), recording item by item whether to adopt each practice and why. These projects were read by subagents fetching the web pages, so the citations are paraphrases, not guaranteed word for word; any of them may also have changed since.

**Adopted (representative items):**

| Practice | From | In TierSpec |
|---|---|---|
| Most changes use a lightweight spec, with rigor added progressively | OpenSpec (Lite / Full) | Tiers A / B / C |
| A change should state its single intent in one sentence; if it needs a lot of "and"s, split it | OpenSpec | "Can be stated in one sentence" in tiering |
| Requirements state at least one "what we won't do", so downstream doesn't fill it in on its own | BMAD (both the v4 and v6 templates), cc-sdd | At least one in Tier B's "Goals and non-goals" and Tier C's "Scope" |
| No guessing where things are uncertain; mark them | Spec Kit (`[NEEDS CLARIFICATION]`) | State the assumption, or list it under open questions with a default approach |
| Success criteria are technology-agnostic and measurable | Spec Kit | Acceptance criteria are "one verdict each" |
| Completion evidence must be freshly produced on the current code state, and conclusions can't be bigger than the evidence | cc-sdd | "Completion check" in this chapter |
| When changing old behavior, explicitly mark additions, modifications and removals | OpenSpec | Mark each item "Added / Modified / Removed", cite the old acceptance-criterion number, wait for the human to nod |

**Not adopted (representative items):**

| Practice | From | Why not |
|---|---|---|
| Maintain a "current spec library" and automatically merge changes into it on archive | OpenSpec | It would create two sources of truth for "the current state" alongside the living docs (Chapter 8) |
| A separate "constitution" file, with a version number and amendment rules | Spec Kit | It duplicates the rule files and becomes a copy of the rules (Chapter 4) |
| Tests are optional, written only when the requirements explicitly ask | Spec Kit | Conflicts with "bug fixes start with a failing test" and "every task carries a verification" |
| A dedicated clarifying-questions stage before writing requirements | Spec Kit | No separate stage; ambiguities become assumptions or open questions; its sweep dimensions (non-functional, external dependency failure, consistent terminology, and so on) were folded into the requirements self-check (see "Structure of Tiers B and C" in this chapter) |
| User stories ranked P1 / P2 / P3, each shippable independently | Spec Kit | Serves multi-person, staggered releases; large requirements are already handled by "split into several specs" |
| Project memory files (product, tech, structure, roadmap) | cc-sdd and others | Duplicates the always-on rules and the living docs |
| Effort estimates on tasks | spec-workflow-mcp | Meaningless for agent execution; size is controlled by task-count thresholds |

The author's project also ran a retrospective on its own old specs (subagents sampled and scored them, so it's a subjective estimate), and the conclusions went into the rules as well: fewer than half of user stories carried useful information, so by default they aren't written and the motivation goes into the background; EARS phrasing (requirements written in the form "When …, the system shall …") is used only as needed, where there are many states, time windows or branches.

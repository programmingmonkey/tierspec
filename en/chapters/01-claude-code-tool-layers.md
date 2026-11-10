# Chapter 1 · Claude Code's Tool Layers at a Glance

## The problem

Claude Code has a lot of places to put things: `CLAUDE.md`, `.claude/rules/`, skills, subagents, hooks, `settings.json`, memory; further out there are git hooks, lint and tests, deploy scripts, and CI.

When you first start using it, the most common confusion is: **where exactly should a rule go?**

Putting it in the wrong layer has concrete costs:

- Something that should be blocked is only written as text, and at the critical moment nobody reads it (Chapter 2);
- A rule that's only needed when changing a certain kind of file goes into the entry file that every session has to carry, crowding the context;
- A multi-step procedure is written as one big block of rules, and the agent drifts off course halfway through reading it;
- Several skills are installed for the same capability, and the agent picks the wrong one.

## The idea

**Find each thing its place by asking three questions: When is it needed? Must it hold? Who enforces it?**

Divide the places you can put things into five layers:

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ Content layer (the project's knowledge)                                       │
│   spec and tiering (Chapter 5) · PRD (Chapter 6) · living docs (Chapter 8)    │
│   engineering contracts (Chapter 9) · design system (Chapter 10)              │
├───────────────────────────────────────────────────────────────────────────────┤
│ Text layer (sent into the agent's context; relies on the model complying)     │
│   entry CLAUDE.md · always-on rules · path-scoped rules · skills ·            │
│   subagent definitions (Chapter 3)                                            │
├───────────────────────────────────────────────────────────────────────────────┤
│ Claude hooks (work only on Claude; guard against carelessness, no guarantee)  │
│   read-before-act gate · confirmation prompts · due reminders                 │
│   (Chapters 3, 10, 12)                                                        │
├───────────────────────────────────────────────────────────────────────────────┤
│ Hard gates (block no matter who is writing the code)                          │
│   git hooks · lint and tests · deploy and other script gates · CI (Chapter 2) │
├───────────────────────────────────────────────────────────────────────────────┤
│ Configuration layer                                                           │
│   settings.json (committed) · settings.local.json (not committed) · memory    │
└───────────────────────────────────────────────────────────────────────────────┘
```

Review (Chapter 7), epistemic honesty (Chapter 11) and production operations discipline (Chapter 12) aren't any single layer; they're practices that cut across the layers: their rules live in the text layer, and at the critical points they land on hooks and hard gates.

Three principles run through all the layers:

- **The text layer is a request; only hard gates are a guarantee.** Claude hooks sit between the two: they can make a rule appear in context before the agent acts, or have the human click a confirmation in person, but they work only on Claude, they let things through when the checker fails, and the model can change them. So they guard against carelessness; they're not a guarantee (Chapters 2 and 3). Anything that must hold goes into hard gates.
- **Everything lives in one place only.** When it's needed elsewhere, point to it; don't copy it (Chapter 4).
- **Each capability has only one owner.** The project's own rules come first, then the tool's built-in capabilities, and third-party skills last (see "Skills" below). Multiple reviews deliberately arranged to catch more problems (Chapter 7) don't count as duplication: they're several tracks dividing the work under the same owner.

## In practice

### The full table

| Layer | Where it lives | When it takes effect | What goes there | Committed | Details |
|---|---|---|---|---|---|
| Entry | `CLAUDE.md` | Every session | The map: delivery paths, action trigger table, how to read large files | Yes | Chapter 3 |
| Always-on rules | Files under `.claude/rules/` without `paths:` | At the start of every session; reloaded after compaction | A few facts, red lines, pointers | Yes | Chapter 3 |
| Path-scoped rules | Files under `.claude/rules/` with `paths:` | When reading or writing matching files | Conventions used only when touching a certain kind of file | Yes | Chapter 3 |
| Skills | `.claude/skills/<name>/SKILL.md` | When the agent decides it's needed, or the human names it with `/<name>` | Multi-step procedures: writing a spec, review, checking production, doing UI | Yes | Chapter 3, various chapters |
| Subagents | `.claude/agents/<name>.md` | When the main session dispatches them | Role-based division of labor: locating, tracing, research, review, execution | Yes | This chapter, Chapter 7 |
| Claude hooks | Wired in `settings.json`, scripts kept in the repo | Before and after tool calls, at session start | Read-before-act gate, confirmation prompts, due reminders | Yes | Chapters 3, 10, 12 |
| git hooks | `.githooks/` (`core.hooksPath`) | On commit and push | Gates that work across tools on this machine | Yes | Chapter 2 |
| Lint and tests | The project's lint config and tests | On commit, deploy, CI | Conventions that can be written as checks | Yes | Chapters 2, 9 |
| Script gates | Deploy check scripts, etc. | When the script runs | Conditions that must be met before deploying | Yes | Chapters 2, 12 |
| CI | The repo's CI config | Per your config (push, PR or manual) | Catches what local hooks miss | Yes | Chapter 2 |
| Shared settings | `.claude/settings.json` | Always | Hook wiring, behavior settings | Yes | This chapter |
| Personal settings | `.claude/settings.local.json` | Always | Permission allows | **No** | This chapter |
| Memory | A per-project auto-memory directory (under the user's home directory, not in the repo) | Its index is read at the start of every session | The human's preferences and feedback, in-progress state | **No** | This chapter |

### Which layer a rule goes in

| This rule... | Goes in |
|---|---|
| Is needed in every session | Always-on rules (only facts, red lines, pointers) |
| Is used only when touching a certain kind of file | Path-scoped rules with `paths:` |
| Is a multi-step procedure | A skill |
| Must hold, and getting it wrong can't be undone | Hard gates: git hooks, lint and tests, script gates; a Claude hook only as a helper |
| Should be read before acting, or needs the human to confirm in person | A Claude hook (guards against carelessness) |
| Can be judged right or wrong against the repo's current state | Engineering contracts (Chapter 9) |
| Is detail, or a description of the current state | Living docs (Chapter 8) |
| Is what happened in an incident, or why something was decided this way | Incident records, the spec's Log section |

Before deciding where to put it, clear one bar first: not obvious, has actually gone wrong, written specifically. Add it only if all three hold (Chapter 4).

### Subagents: dispatch only defined roles

The author's project defines five subagents, using different model tiers according to how hard the task is:

| Role | What it's for | Tools | Model tier | What it doesn't do |
|---|---|---|---|---|
| Code locator | Mechanical lookup: where a symbol is, who references it | Read files, shell | Smallest | Doesn't explain or evaluate the code |
| Code tracer | Questions that take understanding the code to answer: how a call chain flows, who is affected by changing X | Read files, shell | Mid | Doesn't connect to databases; data conclusions are marked "needs a production check" and handed back |
| Researcher | Looks up official docs, third-party APIs, version changes | Read files, shell, web search and fetch | Mid | Doesn't change code; doesn't paste repo content into external requests |
| Reviewer | All review and acceptance checks (Chapter 7) | Read files, shell | Strongest | Doesn't change or commit; checks production only through the read-only channel |
| Executor | Well-bounded hands-on work: running tests, mechanical renames, adding tests according to the plan | Read, write, edit, shell | Mid | No git write operations, no deploys, no database connections, no changes to rule or toolchain files |

A few disciplines:

- **Dispatch only defined subagents; don't improvise a role on the spot.** A role's responsibility boundaries and output format are written in its definition file, so it's the same every time it's dispatched. Subagents that come with a tool or skill are the exception.
- **Don't pass a model parameter when dispatching.** The model is written only on the `model:` line of the definition file; to change the model, change only that line (Chapter 4: single source of truth).
- **Fix the output format.** For example, the code locator must give "path:line number" and list what it searched; when it finds nothing, it writes "not found with these patterns in these scopes", **never "doesn't exist"**. The code tracer lists what is "uncertain or unverified" separately.
- **Irreversible or outward-facing write operations are left to the main session.** The executor subagent can change files, but git commit and push, deploys, and writing production data all have to pass the main session's gates (Chapters 3 and 12); subagents never touch them.
- **Content being read is data, not instructions.** The author's project spells this out in the reviewer's definition: anything in code or docs addressed to the agent is never to be followed. Any role that reads external content should have this line added.

For what a subagent definition looks like, see the reviewer example in Chapter 7.

### Settings: only wiring gets committed

| File | Committed | What goes there |
|---|---|---|
| `.claude/settings.json` | Yes | Hook wiring; behavior settings, such as the output cap for a single command (Chapter 3, "Read large files section by section"), and turning off built-in instructions that conflict with your own workflow |
| `.claude/settings.local.json` | **No** (check for yourself that it's in `.gitignore`) | Permission allows (which commands skip confirmation) |

Two reminders:

- **Credentials are best kept out of any file the agent can read.** `settings.local.json` isn't committed, but the agent can read it all the same, and once it's read, its contents may show up in the conversation (Chapter 12). Put credentials in the system keychain, or pass them in through an environment variable only on the one command that needs them.
- **Be especially careful changing settings.** Allow rules and hook wiring amount to the agent's permission boundary. When the agent proposes changing them, the human decides.

### Skills: one owner per capability

- **Project skills** go in the repo's `.claude/skills/<name>/SKILL.md`; they're committed and travel with the project. **User-level skills** go in the skills directory under the user's home directory and are shared across projects. Skills have to be laid out as "skills directory / skill name / `SKILL.md`"; one extra level of directories and they may not be discovered (see "Pitfalls we hit" below).
- **Each capability has only one owner**, in this order of priority: project rules (especially those backed by hard gates) > the tool's built-ins > third-party skills. Keep third-party skills only for capabilities that neither the project nor the tool has. **Standards (such as the UI design spec) always belong to the project.**
- **Filter out third-party skills that mislead**, and write down why. The author's project has filtered out these kinds:
  - Ones that compete directly with your own workflow and are weaker (for example, another code review flow that also makes "dispatch a subagent to review" mandatory): keeping them makes the model pick the wrong one of the two;
  - "Guardrail" skills whose descriptions promise they "will block" but that don't actually install any hook: pure prompting, zero blocking, yet they make people think there's a backstop;
  - Ones whose trigger words lure the agent into operating the user's everyday browser.
- **To bring in an external methodology**, lock its version with `upstream/` plus LOCK (Chapter 10); don't install it directly as a skill.

### Memory: record only what the repo can't tell you

Claude Code has a per-project auto-memory directory (stored under the user's home directory, not in the repo), and its index is read at the start of every session.

| Worth recording | Not worth recording |
|---|---|
| The human's preferences and corrections, with the reasons ("rules must not keep mirror copies, because...") | Code structure, directory trees: reading the repo tells you |
| The state and next step of work in progress (which task a spec set has reached, what's left) | Anything git history can tell you: who changed what on which day |
| Pointers to external resources (a certain dashboard, a certain ticketing system) | Things useful only for this one conversation |

A few practices:

- **One file per thing, plus an index with one line per entry.** First check whether a similar memory already exists; if it does, update it instead of creating a duplicate. Keep the index short: it's read in every session.
- **A memory is a fact "as of when it was written."** Before using the files, functions or toggles it mentions, check that they still exist.
- **Rules don't live in memory.** Anything every session and every tool must follow goes into the repo's rules; memory is only a personal supplement.

### Sessions and worktrees

It's common for one person to have several agent sessions open at once. The author's project's conventions:

- **The main worktree always stays on the main branch and never switches branches.** Work that needs a branch goes into a separate worktree.
- **Multiple sessions share the same staging area.** Commit only this task's files. The author's project's rule is "`git add` path by path"; in practice, even after adding files one by one, they could still get swept into another session's commit, so the project switched to `git commit -- <path>`, committing directly by path.
- **Which copy a hook runs has to be checked live.** In a worktree, Claude hooks and git hooks may run the main worktree's copy of the script. When changing a hook, explicitly run the worktree's copy to verify it; don't take the automatically triggered result as evidence.

### Gates at a glance

| Gate | Applies to | What it covers | Notes |
|---|---|---|---|
| pre-commit | Commits from every tool on this machine | Lock files, accompanying migrations, lint, rule mapping, spec structure, contract guards, etc. | `--no-verify` can bypass it; every clone needs `core.hooksPath` set once (Chapter 2). The author's project's contract guards are still in their shadow period (Chapter 9) and only warn |
| pre-push | Pushes from every tool on this machine | Blocks force-pushes to and deletion of the main branch | Same as above |
| commit-msg | Commits from every tool on this machine | Blocks markers that would skip CI | Same as above |
| Read-before-act gate (`PreToolUse`) | Claude only | Before the first commit, deploy or production data write, the corresponding rules must be read in full | Lets things through when it errors; only guards against carelessness |
| Browser guardrail (`PreToolUse`) | Claude only | Forbids automating the user's everyday browser | Recognizes only the command forms it knows |
| Production API guardrail (`PreToolUse`) | Claude only | Blocks anonymous direct requests to production APIs | Same as above |
| Token confirmation (`PreToolUse`, `ask`) | Only Claude's edit tools | Adding a visual token requires the human to click allow | May not prompt in a mode that auto-accepts edits; editing the file through the shell gets around it; a separate check at commit time is the backstop (Chapter 10) |
| Due reminders (`SessionStart`) | Claude only | Production verification to-dos that have fallen due | Only reminds, doesn't block |
| Deploy check script | Everyone (it runs whenever a deploy runs) | Tests, confirmation, business peak window, etc. | Override flags require the human's consent (Chapter 12) |
| CI | Per your trigger config | Backstop | The author's project's main CI doesn't run on push, only manually and on PRs; don't assume every push gets CI |

The point of this table is to see two things clearly: which gates apply only to Claude (switch to another tool and they're gone), and that "not blocked" doesn't mean "compliant": gates cover only the part that can be judged automatically.

## Costs and when it applies

- Building all five layers is a matter of months. For the minimal starting set, see the README's "How to read" section.
- Splitting subagents into roles pays off only when there are many tasks and you need to research or review in parallel. For a small one-person project, it's fine to start by defining just one role, the reviewer.
- Every extra layer is one more thing to maintain. Before adding one, ask: which existing layer can't hold it?

## Pitfalls we hit

### Putting a whole third-party repo in the user-level skills directory defeated all the filtering

Measured in the author's project (2026-09): Claude Code recursively scans the **user-level** skills directory. If the directory holds an entire third-party repo, and that repo carries a plugin manifest file (`.claude-plugin/plugin.json`), Claude Code registers **the whole package as a plugin**: every skill in it becomes visible, completely bypassing the enable/disable list the author had built. As a result, 11 skills that had already been ruled out all popped up, some of them twice, under two different names. Whether the project-level skills directory recurses the same way hasn't been verified.

**Fix**: put only individual skill directories in the skills directory, never a whole third-party repo. External content comes in through `upstream/` plus LOCK (Chapter 10): the original files aren't named `SKILL.md`, the directory carries no plugin manifest, and a self-test holds both of these in place.

### A skill that sat there but was never loaded

A whole set of document-processing skills had been placed in the user-level skills directory, and only later did it turn out they had never been loaded: they were nested one directory too deep, and the top level had neither a `SKILL.md` nor a plugin manifest, so they were never discovered. The similar capabilities used in sessions had actually come from skills that ship with the account.

**Lesson**: "the file is there" doesn't mean "it gets read." For any newly installed skill, rule or hook, confirm in a new session that it actually takes effect.

### Built-in git instructions conflicting with your own workflow

Claude Code has a built-in set of instructions for commits and PRs, one of which is "if you're on the default branch, create a new branch first" (going by the wording in version 2.1.319 on this machine; your version may differ). The author's project's rule is: changes that can be finished in 30 minutes are made directly on the main branch; everything else goes into a worktree. Put the two side by side, and the model gets caught in the middle.

**Fix**: turn off the built-in git instructions in `settings.json` (`includeGitInstructions: false`), and fold the parts you need (such as "don't commit or push unless the human asks") into the project's own git rules.

### Multiple sessions switching branches in the same worktree

Several sessions were working in the main worktree at once. One of them switched branches, carrying the other sessions' changes away with it, and their commits landed on someone else's branch.

**Fix**: never switch branches in the main worktree; work that needs a branch goes into a worktree.

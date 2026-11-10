# Chapter 9 · Engineering Contracts

## The problem

Every project has a class of rules that take one sentence to state but matter a lot: "React hooks must come before any `return`," "times are always displayed in one specific time zone," "every data panel must declare what it shows when loading fails." What they have in common: **a glance at the code tells you whether it's right or wrong**.

Rules like these usually end up scattered: one tucked into the design spec, one into the backend conventions, another written in some living doc. Some are guarded by a test or a lint rule, some are just text; and for the guarded ones, nobody can say whether the guard is still there or whether it guards this particular rule.

## The idea

**Engineering invariants that can be judged right or wrong against the current state of the repo get split out as "engineering contracts": one file per contract, each registering its machine guards; any part that isn't guarded is explicitly marked "text only."**

- **Contracts govern "how the code must be written"; the design system governs "what the interface looks like."** The two are peers, and neither carries content belonging to the other (Chapter 10).
- **Guards must be registered, and the registration must be verifiable.** Writing "there's a test guarding it" isn't enough; say which file and which part, and let a self-test prove it's still there.
- **"Text only" is nothing to be ashamed of; hiding it is what's dangerous.** When you state plainly which part isn't guarded, readers know that part relies on discipline alone, and they know where to add a guard.
- **Classify by "who can violate it,"** not by "which side's code the rule is written in."

### Where they live and how they're classified

```
contracts/
  README.md            How to write one, the template, guard registration rules, what the self-test checks
  frontend/<name>.md   Only frontend code can violate it
  backend/<name>.md    Only backend code can violate it
  shared/<name>.md     Both sides can violate it (a definition one side produces and the other consumes, or a convention each side must keep): written only once
```

In each contract's front matter, "applies to" takes one of "frontend," "backend," or "both," corresponding to `frontend/`, `backend/` and `shared/` respectively; the self-test checks that the two match.

### What goes into a contract and what doesn't

| In | Not in |
|---|---|
| Invariants that can be judged right or wrong against the current state of the repo: "every X must declare Y," "Z must not be used directly," "W may only be taken from V" | One-off operational discipline (which commands to run, in what order): put it in a skill or an ops doc |
| | Visual values and visual specs: put them in the design system |
| | Incident stories and measurement records: put them in incident records or living docs; the contract only points to them |

Adding a contract clears the same bar as adding a rule: not obvious, has actually gone wrong, and written specifically (Chapter 4). In addition, the rule should in principle be expressible as a machine check, even if for now it exists only as text; anything that fundamentally can't be judged right or wrong stays among the ordinary rules.

## In practice

### What a contract looks like

The file name is the contract name, and the top-level heading matches the file name. Here is `contracts/frontend/hooks-order.md`:

```markdown
---
applies-to: frontend
read-when: writing or changing React components and custom hooks
guard-routes: <frontend-package>/src/**
---

# hooks-order

## Rule

React hooks always come before any `return`; use JSX expressions for conditional rendering, not an early return that skips a hook.

## Why

The cost of a violation is a blank white page; the build only transpiles, and type checking can't catch this kind of control-flow constraint either. Only lint can stop it.

## Machine guards

| Guard | Side guarded | Kind | Enforcement point |
|---|---|---|---|
| `<frontend-package>/eslint.config.mjs#'react-hooks/rules-of-hooks': 'error'` | Frontend | lint | pre-commit, pre-deploy check, CI |

What it can't stop: the dependency-array check (exhaustive-deps) is deliberately not enabled and is outside the guard's scope.

## Exception register

None (this rule has zero exemptions: on a violation, restructure the code; don't add eslint-disable)

## Read before changing the implementation

The header comment in the eslint config (why this rule goes straight to error level).
```

**Five required blocks**, headings copied exactly, none left empty; if there's nothing, write "None":

| Block | What to write |
|---|---|
| Rule | The first paragraph is the **rule's lead sentence**, which is copied verbatim into the index (see below); the rest of the body follows it |
| Why | The reasoning that holds today; for the incident story, only point to the incident record, don't move it in |
| Machine guards | The guard registration table, plus a sentence or two on "what it can't stop" |
| Exception register | Which places are allowed not to follow this rule. Exceptions are best declared in the code (for example a note field on the component); this block only points there and doesn't keep a separate list in the doc |
| Read before changing the implementation | What to read before changing how this rule is implemented: header comments, regression tests, paths to reference implementations |

**Front matter**:

- **Applies to**: frontend, backend, or both, matching the directory it's in.
- **Read when**: which code changes call for reading this contract; it goes into the index's "when to read" column.
- **Guard routes** (optional): which staged files should make the commit step run this contract's guards; see below.

**The rule's lead sentence** has to be machine-checkable, so it gets a few mechanical criteria: it is a body paragraph (not a list, table, quote, heading or code block), it ends with a period, and its length does not exceed a cap (say, 400 bytes). Whether it "can be judged right or wrong and can be understood on its own" is beyond a machine; that relies on the author and on review.

### How guards are registered

- One guard per row, four columns: guard, side guarded, kind, enforcement point.
- **The guard column is written as "path#anchor"**. The anchor is a piece of verbatim text in that file (an export name, a test case name, a lint rule name). The self-test checks that "the path exists and contains the anchor text," so "the file is still there but the guarding part was deleted" also gets caught. If the same rule is guarded by several files (for example, two frontend packages each with its own eslint config), register one row for each.
- **Kind and enforcement point take fixed values**: kind is one of test, compile-time assertion, lint, hook section (a particular check within a git hook script), or runtime assertion; enforcement point is pre-commit, pre-deploy check, CI, or runtime, and more than one may be chosen.
- **Coverage**: every side that can violate this contract must have either at least one guard row or a row "text only: <which part isn't guarded>".
- **Back-link**: for a guard whose kind is "test," the file must state the contract's path at the top. When the test fails, whoever reads it can find their way back to the contract.
- **Below the table, write "what it can't stop"**: a sentence or two stating the limits of this guard.

### The index: one per side, generated, not handwritten

The contract bodies aren't delivered to the agent directly; the index is:

- **One index per side**, each a path-scoped rule file with `paths:` (Chapter 3). The frontend index's `paths:` points at the frontend code, the backend index's at the backend code.
- The frontend index includes contracts in `frontend/` and those in `shared/` that apply to the frontend; the backend index includes contracts in `backend/` and those in `shared/` that apply to the backend. A `shared/` contract is written only once, but both indexes include it.
- Each index entry is one line: contract name, when to read, the rule's lead sentence, guards and enforcement points. The full body is fetched on demand.
- The index table is a **generated block** in the rule file, generated by a script from the contract files; a self-test ensures it matches the generator's output exactly (Chapter 4, "The one controlled exception").

### What the self-test checks

- **Registration**: front matter complete, and "applies to" matches the directory; all five blocks present and non-empty; the rule's lead sentence meets the mechanical criteria; every guard's path exists and contains its anchor; kind and enforcement point have legal values; coverage holds; test guards have back-links; where guard routes are written, every path pattern matches at least one real file.
- **Index up to date**: the generated blocks of both indexes match the generator's output exactly.
- **No dangling references**: every contract path written anywhere in the repo actually exists.

The self-test is wired into pre-commit, so changing a contract, changing a guard file, or deleting a guard file all trigger it.

### Run guards at commit time; new guards go through a shadow period first

"Guard routes" holds one or more path patterns: if a staged file matches, pre-commit runs this contract's guards, so you don't have to run all of them every time. What goes there is the input the guard reads to make its judgment, such as the module under test or the directory where the guard lives.

A guard newly wired into the commit step first goes through a **shadow period**: it only warns, doesn't block, and logs as it goes. After a while, review the log, confirm it judges correctly and doesn't slow commits down, and then switch it to actually blocking. Block from day one, and a single false block trains the habit of "red doesn't matter" (Chapter 2).

## Costs and when it applies

- Each contract is a file, plus guard registration and the self-test, so the cost per contract isn't low. Only make contracts for rules that "have actually gone wrong and can in principle be machine-checked."
- **The self-test only proves that a guard exists, contains its anchor, and has a back-link; it can't prove the guard actually enforces the rule.** Don't read "has a guard" as "safe."
- In the author's project, the commit-step guards are still in their shadow period (started 2026-11), and there's no data yet on how they work once switched to blocking.
- The contract system suits the point where rules have grown numerous enough to be scattered all over. At the start, one path-scoped rule plus a lint rule or two is enough.

## Pitfalls we hit

### Engineering rules mixed into the visual design spec

Engineering behavior rules such as "how to judge the data freshness of a certain kind of panel" and "which day's data to take" were originally tucked into the master design spec for visuals. The master design spec governs what the interface looks like; tucked inside it, these rules were hard to find and had nowhere to register guards.

**Fix**: move these rules out of the design spec into engineering contracts, delivered by path to sessions that change frontend code; the design spec keeps only the visual part and points to the contracts.

### A rule only lint can stop

The hooks order in the example above: its reasoning is in its "Why." This rule really did cause a blank-page incident, so it went straight to an error-level lint rule with zero exemptions and was registered as a contract, so that the agent reads it in the index first when changing components.

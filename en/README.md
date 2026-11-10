English | [中文](../README.md)

# TierSpec

**From requirements to implementation: a tiered AI engineering practice for solo developers.**

TierSpec answers one question: when one person works with an AI coding agent on a real, long-lived project, how do they take an idea all the way from requirements to production without making the project messier with every change?

Like common spec-driven development (SDD), it says "write it down clearly before you build". The difference:

- **Tiers, not one size fits all.** Not every change needs the full process. First do a read-only investigation and give the four-line report, then pick one of three tiers, A / B / C. A change with an irreversible step, trade-offs the human must decide repeatedly, or a need for an audit trail is Tier C; the rest split into A and B by asking "can the fix be stated in one sentence?" and "has the impact been verified?". How heavy the process is follows the tier.
- **Tier C product requirements get a PRD first where possible, then a spec.** New modules and new pages especially. The PRD comes with a prototype; product intent and technical design are written and reviewed separately.
- **Rules must reach the agent, and critical actions must be stoppable.** The spec is only one layer; how rules reach the agent, and how irreversible actions are blocked by machine gates, are just as much part of the practice.
- **Conclusions need evidence.** Data conclusions are checked against production, evidence is logged item by item, and when there is no trustworthy basis, nothing is produced.

This repository covers only **ideas and practices**, with templates and desensitized examples; it ships no framework code. How it maps to Claude Code's official best practices and to other open-source SDD methods, and what it takes or leaves, is in Chapter 5; the skills and design ideas behind the design system are in Chapter 10. The examples use [Claude Code](https://code.claude.com/docs/en/overview), but most of the ideas don't depend on any particular tool.

This English edition is translated from the Chinese edition, which remains the reference version. Terms are fixed in the [glossary](GLOSSARY.md).

## The whole flow

```
Idea
 │  Read-only investigation, four-line report: Root cause or Goal / Impact / Similar cases / Fix
 ▼
Tiering ── A: change directly ─────────────────────────────▶ One commit (four lines in the commit message)
 │
 ├──── B: lightweight plan ── one spec.md (Goals and non-goals / Approach and steps / Log) ▶ Implement → Verify
 │
 └──── C: full process ──┬── Product requirement: PRD + prototype (where possible) ── Requirements review* ── Decision digest
                         │                                                                │
                         │                                                                ▼
                         └── Technical rework / bug fix / engineering task ──▶ requirements → design → tasks
                                                                                          │
                                                                                          ▼
                                 Implement → Code review* → Completion check → Post-release verification → Archive
```

\* The author's self-check is mandatory; the independent reviews marked with an asterisk are called by the human, not run automatically by the agent (Chapter 7).

Running through the whole flow: tool layers (Chapter 1), layered rule delivery (Chapter 3), machine gates (Chapter 2), evidence logging (Chapters 5 and 6) and epistemic honesty (Chapter 11).

## Contents

| Chapter | Topic | In one sentence | Status |
|---|---|---|---|
| [0](chapters/00-grown-from-fupanbao.md) | Grown from Fupanbao | Where this practice came from, and why that project could force it | ✅ Done |
| [1](chapters/01-claude-code-tool-layers.md) | Claude Code's tool layers at a glance | What goes in the entry file, rules, skills, subagents, hooks, settings and memory; which layer a given rule belongs in | ✅ Done |
| [2](chapters/02-written-rules-are-not-enforcement.md) | Written rules are not enforcement | Rules are just text in the context; critical actions need machine gates | ✅ Done |
| [3](chapters/03-how-rules-reach-the-agent.md) | How rules reach the agent | Four channels (always-on, path-scoped, before an action, on demand) and what each carries; with a minimal read-before-act gate | ✅ Done |
| [4](chapters/04-single-source-of-truth.md) | Single source of truth | Each rule lives in one place; the entry file points, it doesn't copy; the bar for adding and removing rules | ✅ Done |
| [5](chapters/05-tiering.md) | Tiering | Read-only investigation and the four-line report first, then Tier A / B / C, then risk add-ons | ✅ Done |
| [6](chapters/06-prd-to-spec.md) | From PRD to spec | Tier C product requirements get a PRD and prototype first where possible: the human writes the intent, the agent fills in and asks, and the decisions become a spec | ✅ Done |
| [7](chapters/07-review.md) | Review | Two independent reviews, with a sample set to measure what review actually catches | ✅ Done |
| [8](chapters/08-living-docs-apart-from-specs.md) | Keep living docs apart from specs | PRDs and specs record what was intended at the time, not how things are now | ✅ Done |
| [9](chapters/09-engineering-contracts.md) | Engineering contracts | Invariants you can check against the repo, each with a registered guard or explicitly marked "text only" | ✅ Done |
| [10](chapters/10-ui-design-system.md) | The UI design system | Tokens are the only source of values; the master design spec and the visual language each own one layer; new design tokens need confirmation first; four modes of work | ✅ Done |
| [11](chapters/11-epistemic-honesty.md) | Epistemic honesty | When there is no trustworthy basis, the right output is no output | ✅ Done |
| [12](chapters/12-production-operations-discipline.md) | Production operations discipline | Keep reads and writes apart; writes need a confirmation phrase, a snapshot and independent reconciliation | ✅ Done |

## Templates and examples

| File | Purpose |
|---|---|
| [templates/prd-template.md](templates/prd-template.md) | PRD template for Tier C product requirements |
| [examples/prototype-theme-ladder-panel.html](examples/prototype-theme-ladder-panel.html) | The interactive prototype that goes with the case study (open it directly in a browser; the data is fictional) |
| [examples/prd-example-theme-ladder-panel.md](examples/prd-example-theme-ladder-panel.md) | A desensitized, trimmed version of a real PRD: from a few lines of raw requirements written by the human, through four rounds of confirmation and the decision digest, to the spec |

## How to read

- No need to read in order. Read Chapter 0 for the background, then Chapter 1 to see what goes in each layer of Claude Code, then "The whole flow", then pick the chapter for whatever hurts in your project right now.
- **Tailor by the criteria; don't copy the rules.** Every rule says what problem forced it. If your project doesn't have that problem, you don't need that rule.
- The rule system grows; it isn't designed in one go. **The minimal starting set** (listed only here in the whole book):
  1. A `CLAUDE.md` that is only a map, plus two or three path-scoped rules (Chapters 1 and 3);
  2. One git hook, such as the main-branch protection in Chapter 2;
  3. Before any change, "give the four-line report, then decide the tier" (Chapter 5);
  4. The floor of epistemic honesty: **check data conclusions against production; if you can't find out, say so; don't make it up** (Chapter 11). Before checking production, set up a query channel with a read-only account (Chapter 12).

  Add Chapter 6 once requirements get complex; add a gate for a class of action once that action has actually gone wrong.

## License

The English edition uses the same licenses as the Chinese edition. See the two files in the repository root:

| Content | License | Full text |
|---|---|---|
| Prose: `README.md`, `chapters/`, the Markdown case study under `examples/` (and their counterparts under `en/`) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-hans) | [LICENSE](../LICENSE) |
| Code and templates: `templates/`, the prototype HTML under `examples/`, `scripts/`, `.githooks/`, `.github/`, and the code blocks in the prose (and their counterparts under `en/`) | MIT | [LICENSE-CODE](../LICENSE-CODE) |

**The prose** may be republished, adapted and used commercially, as long as you give attribution, link to the license and state whether you made changes. Suggested attribution:

> Adapted from [TierSpec](https://github.com/programmingmonkey/tierspec) (author: 任毅 RenYi), licensed under CC BY 4.0.

**Code and templates** may be copied straight into your own projects and modified freely; just keep the copyright notice in `LICENSE-CODE`.

## Contributing

(To be decided)

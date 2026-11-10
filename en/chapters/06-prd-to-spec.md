# Chapter 6 · From PRD to Spec

## The problem

The most common approach for a solo developer is to toss a one-line idea straight at the agent: "Add a panel that shows how themes rotate." (A theme is a market theme or concept that A-share stocks trade on.) The agent quickly hands back a spec that looks complete, or even starts writing code right away.

The problem is that this spec mixes three kinds of things:

- what you **actually want** (the intent);
- what the agent **guessed for you** (defaults, definitions, edge cases);
- the **technical approach the agent settled on along the way** (tables, endpoints, caching).

With all three stirred together, when you review it you can't tell which sentences are yours and which are its guesses. Only after it's built do you discover that a key definition was a wrong guess, and it's already baked into the table schema.

## The idea

**For a Tier C product requirement, produce a PRD with a prototype first where possible, then turn it into a spec. The PRD covers "what we want", the prototype covers "what it looks like", the spec covers "how to build it".**

- **The PRD only describes behavior the user can see and accept.** Technical approaches never go into the PRD; technical constraints the agent discovers in discussion are written only if they affect a product trade-off, and then written as "the cost is that the user will see X". Any technical numbers in the PRD are only suggestions; the spec's design is authoritative.
- **The human writes the intent; the agent completes it and asks follow-up questions.** The background, goals, scope, feature list, and the original requirement under each feature (the bracketed items such as [Layout], [Content], [Interaction]) are written by the human; the agent completes the rest. The agent **doesn't change the human's original text**: additions go below it, and every ambiguity becomes a confirmation item.
- **Every ambiguity needs a human decision, with their own words on record.** Confirmation items have three columns: For your information, Confirmed, Pending. Each Confirmed item keeps the human's own words, so any later dispute can go back to them. When the human's words are just an option code ("pick A", "go with 2"), the decision column must spell out the chosen option in full; otherwise, looking back at their words later won't tell you what was chosen.
- **The decision digest is the PRD's exit.** The PRD's last section compresses every decision into one sentence each; the spec's requirements are rewritten from it, each one citing its source.

### When to write a PRD

| Tier | Product requirement (user-visible behavior changes) | Technical rework / bug fix / engineering task |
|---|---|---|
| A | Not needed | Not needed |
| B | Not needed; quoting the user's own words in the spec is enough | Not needed |
| **C** | **Produce a PRD + prototype first where possible**; especially for new modules and new pages | Not needed; write `requirements.md` directly |

The PRD isn't a gate, it's a tool: Tier C means there's a step that can't be undone, a trade-off that needs repeated sign-off, or an audit trail is needed, and those are exactly the requirements most at risk of having their intent guessed wrong. For a small Tier C change whose intent can be stated in a sentence or two (say, a definition fix that adds a field to an existing page), quoting the human's own words directly in the spec's requirements is fine too. New modules and new pages are different: their layout, states and definitions are all new, and without a PRD and a prototype the agent can only guess.

## In practice

### The life cycle of a PRD

```
The human writes the skeleton (background / goals / scope / feature list / original requirement)
  ▼
The agent completes it: verify the current-state baseline → add definitions, states, edge cases → list Pending items (🔴 blocking / 🟡 has a suggested default)
  ▼
The human answers item by item (writing "Answer: …" under the item; for 🟡 they can just reply "as suggested")
  ▼
The agent moves the answers into "Confirmed" and fills them back into the body; if they raise new questions, start the next round
  ▼  (repeat until layout and definitions have no 🔴 left)
Prototype: build a clickable in-browser prototype with data at close to real scale; questions the prototype raises go back into the confirmation items for another round
  ▼
Requirements review (called by the human; two independent reviews; see Chapter 7)
  ▼
Decision digest → turn into a spec → archive the PRD and the prototype
```

### Pairing the PRD with a prototype

The PRD uses words and ASCII drawings to say "what we want"; the prototype uses a clickable page to say "what it looks like". They're a pair, each covering half:

| | PRD | Prototype |
|---|---|---|
| Single source of truth for | Intent, definitions, rules | Visuals: sizes, column widths, spacing, colors, how each state looks |
| Who writes it first | The human writes the skeleton | The agent builds it from the PRD; the human picks the direction |
| What it catches | Ambiguities, missing states, same name with different meanings | Whether things fit, whether they're legible, whether interactions flow, at real data scale |

A few practices:

- **The prototype is a single HTML file**, opened directly in a browser, with no dependency on the project code. The data is hard-coded in the file, built at production scale (dozens of days, dozens of rows), not just three to five pretty sample rows.
- **Turn the states in the PRD that the human needs to look at into switchable demo toggles**: normal, empty, loading, all empty right after launch… States that occur naturally in the data (say, a day with missing data) don't need their own toggle, but the prototype notes should say which states weren't built. Name each toggle after the PRD item number or acceptance-criterion number, so that later, when comparing state-by-state screenshots against the implementation, they line up one to one.
- **Look at both the light and dark themes**; contrast that falls short should surface at the prototype stage.
- **A prototype overturning the PRD is a good thing**, but it has to go back to the confirmation items for a new decision and be filled back into the body; changing only the prototype isn't enough.
- Companion example: [prototype-theme-ladder-panel.html](../examples/prototype-theme-ladder-panel.html) (the data is fictional).

### The PRD skeleton

The full template is in [templates/prd-template.md](../templates/prd-template.md). What each section is for:

| Section | Who writes it | What it covers |
|---|---|---|
| 1 Overview | The human; the current-state baseline is added by the agent | Background, goals, scope; the agent verifies "what already exists", each item tagged with source and date |
| 2 Feature list | The human starts it, the agent completes it | One feature per line; the phase plan later is sliced along it |
| 3 Functional requirements | The human writes the bracketed [ ] items, the agent adds below them | Layout, legend, definitions, data volume and overflow, state table, relationship to existing concepts |
| 4 Non-functional requirements | The agent drafts, the human confirms | Only what the user can accept: timeliness, what they see on failure, who can see it, how long they wait |
| 5 UI/UX design | — | Points to the prototype; the prototype is the single source of truth for visuals |
| 6 Development phase plan | The agent drafts, the human confirms | Every phase must be releasable on its own, and able to answer "who verifies it, and what do they verify" |
| 7 Confirmation items | Both | For your information / Confirmed (with the human's own words) / Pending |
| 8 Decision digest | The agent | One sentence per item, with its source; the skeleton of the spec's requirements |

### Rules that are easy to get wrong

- **The definitions table must answer for every single number.** Every number and every label on the panel has to answer: what it means, as of what point in time it's calculated, and which existing panel it shares a definition with. Where unsure, write "?" and let the agent look it up. A lot of rework comes from "same name, different meaning": the same word means something else on another page.
- **States are filled in from a table, not just the normal state.** Data not ready, partially ready, historical day, non-trading day, dates before launch that have no data, loading, request failed: every row has to say "what's displayed".
- **The current-state baseline must be verified, and it's only a basis for discussion.** Data conclusions are checked against production, not the local database. When it goes into the spec, the evidence has to be recorded again, because between finishing the PRD and starting the spec, the current state may have changed.
- **Confirmation items share one incrementing number sequence.** If Confirmed and Pending each number their own items, sooner or later the same number will point to different things, and the body is full of cross-references like "see 7.2-N". New items always take "current highest number + 1", and an item keeps its number when it moves columns.
- **The phase table doesn't accept adjectives.** "Basically done" or "mostly usable" isn't acceptance; a phase that can't be written as "can ship on its own" gets merged into an adjacent phase or re-sliced. Anything depending on something not yet live gets its own "prerequisite" row.
- **Don't add a "won't do" list to the PRD.** When completing the PRD, the agent doesn't add "won't do" items; the scope is defined by the body and the decisions, and exclusions in old documents can't be used to veto a new requirement. This rule applies only to the PRD: once it's turned into a spec, the spec's requirements still need at least one non-goal ("what we won't do") to draw the boundary for the implementer (Chapter 5).

### Turning it into a spec

1. **Rewrite from the decision digest; don't copy whole passages.** Every requirement in the spec cites its source, for example "Source: PRD decision 8-3".
2. **Keep the human's own words verbatim.** When quoting the user's own words or a PRD item, don't change a word; mark refinements and additions separately.
3. **Reference the PRD by file name only, without the directory.** Once done, the PRD gets archived to another directory, and a path that includes the directory breaks the moment it's archived.
4. **When they conflict, the spec wins, and the PRD gets corrected.** New facts discovered after spec work starts are filled back into the PRD's confirmation items, so the two documents don't tell different stories.
5. **The phase table becomes the spec's phasing table.** If it needs to be split into several specs, the split and the release order go into the topic README ("Structure of Tiers B and C" in Chapter 5).

## Costs and when it applies

- A serious PRD takes several rounds back and forth, from a few hours to a day or two. Use it only for Tier C; forcing a PRD onto Tier A or B brings back the "waterfall feel" that SDD is most criticized for.
- The human has to actually answer the confirmation items. If the human doesn't answer, or always says "whatever you think", the PRD degrades into the agent asking and answering itself, which is more dangerous than having none, because it looks as if things were decided.
- The PRD is intent, not current state. After launch it's a historical document; to judge "what it looks like now", look at the source code and the living docs (Chapter 8).

## Pitfalls we hit

### Behind one line of original requirement, a state machine

In the [case study](../examples/prd-example-theme-ladder-panel.md), the human's original requirement was only a dozen or so lines: dates on the horizontal axis, levels on the vertical axis, up a level on a gain of more than 3%, down a level on a drop of more than 3%. While completing it, the agent found that "level" is **cumulative state**: today's level depends on yesterday's level. That brought out a string of questions the original text didn't address but that had to be decided:

- If a theme disappears for a few days mid-way and then comes back, where does its level start from?
- Can the algorithm demote a theme all the way down to "out"?
- If someone manually changes the level on a given day, should the later dates be recalculated?

Left for the agent to guess while writing code, every one of these would have become a default value in the table schema. The PRD turned most of them into four rounds and more than twenty confirmation items, each with the human's own words on record.

But not all of them. "If someone manually changes a day's level, should later dates be recalculated" was raised by the agent inside the definitions and confirmed together with a whole group of definitions; there are no separate words from the human on it. By the rules it should have been its own confirmation item. The case study flags this gap honestly (decision 8-6), which also shows that a rule being written down doesn't mean it won't be missed in execution, and that's exactly why requirements review exists (Chapter 7).

### Prototypes overturn the PRD

In the same case, the first version of the prototype built only 12 themes (production has far more), so the measured height came out clearly too small; rebuilt at production scale, the panel was about 1745px tall, far more than one screen, and the original "no collapsing, no scrolling inside a level slot" had to gain an exception. So build prototype data at production scale. The prototype also proved that the "next trading day" column wasn't needed at all. **The PRD fixes the intent; the prototype tests what that intent looks like with real data.** When they conflict, go back to the confirmation items for a new decision, rather than quietly changing one side.

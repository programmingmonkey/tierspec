# Chapter 10 · The UI Design System

## The problem

When you have an agent build UI, the two most common results are:

- **It looks AI-made at a glance.** Every block of content is wrapped in the same rounded card with a faint shadow, with cards nested inside cards; big gradient headings; a row of "big number + small label"; an icon in front of every heading; sections fading in one by one. None of it is ugly on its own, but in a tool people use every day, it's all noise.
- **The visuals slowly drift.** When the agent can't find a suitable color, it defines a private one inside a component; the next session defines another, similar one. A few months later, the same "warning" might come in five shades of yellow.

Add the situation described in Chapter 9: engineering behavior rules tucked inside the visual spec, making it tiring to read both for whoever is changing styles and for whoever is changing logic.

## The idea

**Layer the design system so each layer holds only one kind of thing; follow the axes that are fixed, and be free only on the axes left open.**

In this chapter, "the human" means the project owner, the person who makes the calls for the agent.

In the author's project, what has to be upheld when building UI settled into seven layers:

| Layer | What it holds | Examples |
|---|---|---|
| ① Tokens | Visual values such as colors, shadows, and spacing; **values live only here** | CSS variables in the stylesheet |
| ② Visual language | Style intent: what it looks like, and why | Overview, principles, prohibitions, the "AI default look" blacklist, good and bad samples |
| ③ Master spec and page overrides | Component specs (sizes, forms), plus each token's name, purpose, and where it's used; token values are not copied | The master spec (a large file, read section by section); `pages/<page>.md` only overrides the master spec |
| ④ Engineering contracts | How the code must be written | Not part of the design system but a peer of it (Chapter 9); listed here only because it also has to be upheld when building UI |
| ⑤ Design skill | Working method: which document to read, and in what order to work | Four modes: explore, converge, implement, review |
| ⑥ Review mode | The detailed rules for the "review" mode in ⑤ | Two tracks: gathering evidence and design judgment |
| ⑦ Machine gates | The few things that must hold | Token admission, hardcoded color checks |

Three principles run through all of it:

- **Rules come in two layers: red lines and style principles.** Red lines apply at every stage, and a violation must be fixed; examples are using only registered tokens, never inverting a domain convention (Chinese market software uses red for up and green for down, so red can only mean up), and the engineering contracts. Style principles become the standard only in the converge and implement stages; in the explore stage they are used only to annotate "which of these this option deliberately breaks, and why", not to trim or rework options. This split was added only after a failed blind comparison; see "Pitfalls we hit" below.
- **The master spec, the visual language, and the page overrides are the agent's brief (the design assignment).** To borrow the wording of Anthropic's official frontend-design skill: follow the axes the brief fixes, and be free only on the axes it leaves open. An "axis" is one aspect of the interface that can vary independently, such as color, font size, or density; see "Axis table" below.
- **New tokens are confirmed by the human first.** If no suitable token exists, stop and ask the human; don't add one, and don't define a private one.

## In practice

### Visual language: a document about "why"

The master spec covers component specs and how tokens are used (how tall this button is, which token goes where); the visual language covers intent. Its structure:

- **Overview**: what the product is, who uses it in what situations, and the overall feel it needs. The first item in the author's project's overview is "industry convention first": when convention conflicts with general design principles, convention wins.
- **Principles**: each one is labeled with its "layer" (red line or style principle) and its "scope" (whole page, between panels, inside a panel, field), and spells out "how to judge it": what full marks look like, and what a violation looks like. The author's project's principles (numbered 1–10, with No. 1 split into three; "Sources and comparisons" below refers to them by these names):

  | Principle | In one sentence |
  |---|---|
  | Fixed-layout pages have a clear primary | The whole page has a single primary area; the most important content sits at the top or left, takes the most space, and has the strongest contrast |
  | Panels on assembled pages are peers | On a page users assemble themselves, no panel grabs attention with large color blocks, heavy decoration, or oversized numbers |
  | One focus per panel | Each panel serves one main task and has only one visual focus; everything else steps down a level |
  | What goes in a panel | Placed by frequency of use: the most used on the first layer, at most one more level behind a click |
  | Every field is useful and has a baseline | Every field first answers "what decision do I make from this"; every number has a visible comparison baseline next to it |
  | Like things alike; group with whitespace first | Fields of the same kind share position, precision, and units; group with whitespace first, and use containers last |
  | One meaning, one hue | One meaning, one hue; key states have a second channel besides color |
  | Up/down colors mean only up/down | The industry's conventional direction colors are not lent to any other meaning |
  | A few density levels | Only two or three density levels, uniform within a panel |
  | Hierarchy uses only four means | Only font weight, font size, text darkness, and surface lightness |
  | Motion only expresses state | Only changes triggered by user actions may be animated, and exits are faster than entrances |
  | One active-state style site-wide | Selected and active styles are the same across the whole site |

- **Prohibitions**: styles that are explicitly unwanted.
- **The "AI default look" blacklist**:
  
  | Look | Why it doesn't work in a tool-style UI | Replace with |
  |---|---|---|
  | Every block wrapped in the same rounded card with a faint shadow; cards inside cards | Containers inside containers only add border noise | Group with whitespace and light dividers |
  | Gradient text, big gradient headings | Lowers readability, and the gradient itself carries no information | Emphasize with font weight or size |
  | A row of side-by-side "big number + small label" | Big numbers side by side mean there is no focus | At most one focal number per block, with a baseline |
  | Rainbow categories, one bright color per category | With that many colors, no color can signal importance; they also collide with semantic colors | Distinguish with text first; when color is needed, use weak emphasis |
  | An icon in front of every heading and field, or emoji used as icons | Icons that carry no information are noise; emoji render differently across platforms | Use icons only when they represent an action or a state, from a single icon library |
  | Empty states with only an illustration, or just "No data" | Doesn't say why it's empty or what you can do | State the reason and the next step |
  | Sections fading in one by one, numbers rolling up from 0, redrawing on every refresh, always-on pulsing dots | On a UI people look at every day, decorative motion is just delay | Remove it; keep only short transitions on user actions |
  | A thick colored bar on the left of a card | The most typical AI look, and it gets read as an alert | Express it with text, an icon, or font weight |
  
- **Good and bad samples**: point out which part of the product is a good example and which is a bad one, and why.
- **Known conflicts**: when the visual language and the master spec conflict, log it here for the human to decide; neither side wins by default.

### Axis table: what's fixed, what's free

Break the interface into a number of "axes" and write down, for each stage, whether each axis is fixed or open:

| Axis | Exploration | Convergence and implementation |
|---|---|---|
| Color and semantics | Open (how strong the colors are, whether to use category colors); only red lines apply | Fixed |
| Typeface and font size | Typeface fixed; font size chosen from the registered steps | Fixed |
| Spacing, corner radius, shadow | Open within the tokens | Fixed |
| Component form | Open: new forms may be proposed; conflicts with the master spec go to the human during convergence | Fixed |
| Engineering behavior | Fixed (red line) | Fixed |
| Information structure within a panel, focus, which fields to keep, empty-state copy, interaction details | Open | Free within the principles |

External methodologies apply only to axes that are open or left empty at the current stage; wherever they conflict with a fixed axis, your own spec always wins.

### Token admission: three gates

"Don't let the visuals drift" is a rule the project owner set. Written only as text, the agent might still casually add a token when it can't find a suitable one (Chapter 2: written rules are not enforcement), so it became three gates:

1. **Claude-side hook**: a `PreToolUse` hook on the edit tools that watches only two files: if an edit to the token definition file adds or changes a token, or writes a new color value that isn't a token into the theme config file, it returns `ask`, and a prompt asks the human to click allow. It's written the same way as the minimal implementation in Chapter 3, with `deny` swapped for `ask`. Of the three gates, this is the only one that can actually enforce "the human confirmed it", but it covers only the edit tools: if the agent edits the file with a shell command, it gets around it, so it guards against carelessness, not malice (Chapter 2).
2. **pre-commit**: blocks a new token that hasn't been registered in the master spec, or a non-token color value newly appearing in the theme config. It also blocks if the check itself failed to run. It only checks "was it registered", not "did the human confirm it".
3. **lint**: scans every changed UI file for hardcoded colors, color function literals, privately defined color variables, and emoji. The first two gates watch only the token and theme files; colors in all other files are caught by this one.

Once the human confirms, add the token and register it in the master spec in the same commit, with a commit message like "Add token X, confirmed on <date>".

The few things the machines can't police (typefaces, corner radius, motion, primary vs. secondary) are left to the pre-delivery self-check and to review.

### Four modes

| Mode | When | What it does |
|---|---|---|
| **Explore** | A new panel, a new page, or redoing a block | Produce **3 low-fidelity candidates**, each covering only the default state plus two or three key states. The candidates differ clearly on at least two of three dimensions: layout structure, how information is encoded, and color intensity; at least one of them leans bold and color-heavy. Only red lines apply; style principles are used only for annotation. Hand them to the human to pick one or combine several |
| **Converge** | After the human settles on a direction | Produce one complete prototype: covering every state, in both light and dark. Self-check against all the principles; conflicts with style principles are not automatically resolved toward the restrained side but listed for the human to decide |
| **Implement** | After the prototype is finalized | Uphold the master spec, page overrides, and engineering contracts; check both light and dark |
| **Review** | Self-check before delivery; the full two tracks when the human asks | See below |

How this relates to the PRD process in Chapter 6: exploration comes after the PRD's layout and definitions have been pinned down; candidates can be low-fidelity, but their data is generated at production scale; the version that comes out of convergence is the prototype that Chapter 6's "PRD with a prototype" refers to (single-file HTML, data at realistic scale, demo toggles). A redesign adds a new version and doesn't delete the old one: after the human picks, the rejected candidates are kept too.

### Review: two tracks, report leads with conclusions

What's reviewed here is the UI itself, not the kind of design review of design documents in Chapter 7. The division of labor between the two tracks is different too: one track gathers deterministic evidence, the other makes judgments; they complement each other, rather than being two reviewers doing the same thing.

| Track | What it does |
|---|---|
| **Gathering evidence** (deterministic, reproducible) | Take one screenshot each in light and dark, and run one accessibility scan (axe) on each; run the design lint; screenshot each state via the prototype's demo toggles; walk through the interaction along the main task's flow: keyboard focus, loading and failure states, undo, click targets, form errors, extreme data |
| **Design judgment** (independent subagent) | Give it only the visual language, the relevant sections, the screenshots, and the code paths, **not the first track's conclusions**; it scores each principle in the visual language 0 / 1 / 2, with evidence for every score (a screenshot location or file:line); for prohibitions and the blacklist it reports only hit or no hit |

The report format was "taught" by the project owner (see "Pitfalls we hit" below):

- **The first line is a degradation statement**: if everything ran, write "everything ran"; if something didn't, say which item and why (for example, the dark screenshot actually scanned the light page).
- **Right after it come 3–5 conclusions**: the problem, where it is, the suggestion, red lines first. A reader who reads only this block should still know whether to change anything and what. Details go after.
- **Scores have no pass mark**: scores are for comparing and locating problems, not a gate.

### Bringing in upstream methodology: version lock, review the diff before updating

External design methodologies (such as the official frontend design skill, or a community method for cutting animation) are useful, but they weren't written for your product. What the author's project does:

- The original text goes into an `upstream/` directory, unchanged word for word; a LOCK file records the source repo, the commit, and each file's sha256.
- A separate OVERLAY rules section by section on "use as is / adapt / not applicable", and the agent reads only the sections ruled use-as-is or adapt.
- The original files are not named `SKILL.md`, so they don't get registered as standalone skills.
- When updating, first pull the diff and show it to the human, and replace only after the human nods; hand-editing the original text or the LOCK makes the self-test go red.
- Keep the original authors' licenses; write a separate NOTICE stating each original's source and how it was brought in.

## Costs and when it applies

- The seven layers grew gradually out of a long-maintained product. When starting out, one token file, a short visual language that spells out the "red lines" and the "blacklist", and one lint rule for hardcoded colors will stop most of the problems.
- Producing 3 candidates during exploration is much slower than producing a single version; use it only for new panels and new pages.
- A full two-track review means screenshots, scans, and dispatching a subagent each time; do it only when the human asks.

## Pitfalls we hit

### The new process lost a blind comparison

After the new design process (visual language + design skill) was built, it was put up against the old process in a blind comparison on a real panel: each side produced a prototype, traces of origin were removed, they were randomly labeled A and B, the mapping was sealed with only its hash published, and the project owner chose blind. The comparison had two rounds: first a choice based only on the two prototypes, then a final choice after reading the reference review reports. Both rounds picked the old process's version.

The retrospective separated its sources:

- [owner's reasoning, paraphrased] The old process's version won on: numbers written directly inside the bars; different states distinguished by color; the core judgment carrying a colored label; one key action made into a toggle.
- [inference] Two of these were exactly what the new process had deliberately removed under the visual language's rules (business colors that operations staff configure in the admin console and that ship with the data; color meaning only up/down), and the review had also flagged them as problems; "numbers inside the bars" had been moved into a popover by the new process. So the main reason for the loss appears to be that the rules themselves were too restrained, not the toolchain.
- [fact] Each process reviewed both versions, four reference review reports in total, each 13–17 KB, and none had a one-page conclusion.
- [owner's words] "These four reviews have too much in them, I couldn't find the point, I didn't read them carefully."
- [inference] The reference review reports played no part in this choice.

One panel and one blind comparison don't settle anything. After reading the retrospective, the project owner decided to keep the new process but adjust it according to the retrospective; one line in their own words was "the design can be more open at the start". Three things changed after that:

1. **Design splits into three stages, explore, converge, and implement, with openness tightening at each stage**: exploration produces several very different candidates for the human to pick from. This is where this chapter's four modes came from.
2. **Rules split into two layers, red lines and style principles**: exploration upholds only red lines; style principles are used only for annotation, and conflicts go to the human rather than being automatically resolved toward restraint. When the human repeatedly chooses to break the same style principle, change that principle itself.
3. **Review reports lead with conclusions**: a degradation statement on the first line, immediately followed by 3–5 conclusions, details after.

**Lesson**: a design spec makes trade-offs on the human's behalf. When the spec conflicts with the human's actual preferences, it's the spec that has to change, and there has to be a way to discover that conflict, such as this blind comparison.

## Sources and comparisons

### Which skills and design ideas

This design system wasn't written out of thin air. When the author's project rebuilt it in 2026-11, it read the sources below. They fall into two kinds: upstream skills whose original text was brought in and ruled on section by section for usability, and design ideas from which only the viewpoints were taken, with the source noted next to whichever principle uses a given viewpoint.

**Upstream skills brought in as original text.** The original text goes into `upstream/` unchanged word for word, version-locked (see the previous section), then ruled section by section on "use as is / adapt / not applicable":

| Source | License | What was adopted | What wasn't, and why |
|---|---|---|---|
| Anthropic's [frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) skill | Apache 2.0 | "Follow the axes the brief fixes; be free only on the axes it leaves open"; real content throughout; "structure is information" and several points on typography; the two-pass process (plan first and self-review against the brief, then build), used only to plan the open axes; "spend your boldness in one place and keep the rest quiet", which maps to "One focus per panel"; how to write interface copy (name things the way users call them, buttons say what will happen, errors say what to do) | The persona of "creating a one-of-a-kind visual identity for each client and daring to take aesthetic risks": the opposite of "industry convention first, working interfaces should be restrained"; landing-page-style hero sections |
| Emil Kowalski's [remove-animations](https://github.com/emilkowalski/skills/tree/main/skills/remove-animations) | MIT | Reversing the burden of proof: animations are removed by default; the decision tree: remove animations triggered by the keyboard, on high-frequency actions, and on data, except those showing real changes in values; before removing, check whether any code is waiting for the animation to finish | The durations and easing values it gives: our own tokens take precedence |
| Emil Kowalski's [break-ui](https://github.com/emilkowalski/skills/tree/main/skills/break-ui) | MIT | Playing the most difficult real user and testing a piece of UI with the worst data; first check each field's real upper limit, since a mismatch between frontend and backend limits is itself a finding; never truncate numbers, amounts, or dates; stop once the report is done | Putting the worst-case data and the toggles into product code: changed to living only in prototypes or tests |
| Emil Kowalski's [emil-design-eng](https://github.com/emilkowalski/skills/tree/main/skills/emil-design-eng) | MIT | The order of judgment: should it move → why move → which kind of easing → how fast; the more common the action, the shorter the motion; popups don't scale from zero; overlays expand from the trigger point; animation speed affects the perceived loading speed | The overall philosophy of "beauty is leverage, used to stand out": the opposite of what a tool-style UI is for; spring and gesture animations |

**Design ideas from which only viewpoints were taken, without the original text.** Every principle in the visual language is labeled with its "source", with external viewpoints and the project's own decisions listed side by side. The "Which principle it landed in" column below uses the principle names from the visual language section above:

| Source | Viewpoint taken | Which principle it landed in |
|---|---|---|
| [impeccable](https://github.com/pbakaus/impeccable) | The "working interface" mode: scannable, consistent, and predictable over expressive; brand shows in precise details; headline numbers come with their recent history; motion only expresses state; consistent wording for states, with the accent color reserved for the primary action and the current selection; a set of detection rules for AI looks (cards in cards, gradient text, colored side bars, always-on pulsing dots) | Overview; Every field is useful and has a baseline; Hierarchy uses only four means; Motion only expresses state; One active-state style site-wide; the AI default look blacklist |
| [Vercel Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines) | Every state needs to be designed | The blacklist's "empty states that just say No data" |
| NN/g: [preattentive processing](https://www.nngroup.com/articles/dashboards-preattentive/), [progressive disclosure](https://www.nngroup.com/articles/progressive-disclosure/), [animation duration](https://www.nngroup.com/articles/animation-duration/) | Position and length are the strongest visual channels; color is for distinguishing categories and for emphasis, not for expressing magnitude; disclosure beyond two levels has low usability, so the commonly used goes on the first layer; the more common an animation, the shorter it is, and entrances are slightly longer than exits | One focus per panel; What goes in a panel; Motion only expresses state |
| [IBM Carbon data dashboards](https://www.carbondesignsystem.com/building-blocks/data-visualization/dashboards) | The most important data gets the strongest contrast and the largest area; use whitespace to express relationships | Fixed-layout pages have a clear primary; Like things alike; group with whitespace first |
| [Apple HIG: Color](https://developer.apple.com/design/human-interface-guidelines/color) | Don't use the same color to mean different things; don't rely on color alone to distinguish | One meaning, one hue |
| [WCAG 1.4.1 Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) | There must be a visible alternative besides color | One meaning, one hue |
| [Tufte's sparkline theory](https://www.edwardtufte.com/notebook/sparkline-theory-and-practice-edward-tufte/) | Maximum data, minimum design; use a normal-range band as the baseline; heavy borders weaken the content | Every field is useful and has a baseline; Like things alike; group with whitespace first |
| [Linear's UI redesign write-up](https://linear.app/now/how-we-redesigned-the-linear-ui) | Reduce visual noise in a redesign and return to a more neutral palette | Hierarchy uses only four means |

A few notes:

- **When external viewpoints conflict with industry convention, convention wins.** For example, market software's red for up, green for down conflicts with the use of "red means error" in many general design principles; the author's project follows the convention.
- **This is the author's project's reading at one point in time.** These repos and articles all get updated; if you want to use them, read the original as you find it then, and judge for yourself.
- For which axes upstream methodology applies to, see "Axis table" above.

# PRD-Review-Add Theme Ladder panel (desensitized case study)

> **About this case study**: Desensitized and condensed from a real Fupanbao PRD. The technical design, internal names, code paths and production data details were removed, and numbers are approximate; the structure, the human-written original requirement, and the decision process across four rounds of confirmation are kept.
> The human-written parts are reproduced as written, with only two substitutions: a specific stock name became "a certain stock", and a back-office field name in one quote became "a certain column" (7.2-27). In this English edition those parts are translated from the Chinese original.
> The original was written in 2026-09, when the template still had sections for the data model and APIs; numbering here has been rearranged to follow the current template ([templates/prd-template.md](../templates/prd-template.md)).
> How to read it: first see how short the human's original requirement in §3.1 is, then what the agent filled in from §3.1.1 onward and how the human decided in §7, and finally how §8 and the appendix turn into a spec.

> The version table is an excerpt: the prototype details of V1.7 and V1.8 are omitted.

| Doc version | Revised on | Revised by | Changes |
|:--- |:--- |:--- |:--- |
| V1.0 | 2026-09-07 | Human | Created the document |
| V1.1 | 2026-09-07 | agent | Filled in every section; verified the current-state baseline; flagged the core risk that "a level is cumulative state" |
| V1.2 | 2026-09-07 | agent | Backfilled the 14 answers from round 1; raised 7 pending items for round 2 |
| V1.3 | 2026-09-07 | agent | Backfilled round 2's answers: the algorithm can lower a level no further than 1; out only manually |
| V1.4 | 2026-09-07 | agent | Backfilled round 3's answers: up/down can't be entered manually; themes at the same level stack vertically |
| V1.5 | 2026-09-07 | agent | User-facing prototype done; at real scale the panel is about 1745px tall; proposed panel-level scrolling |
| V1.6 | 2026-09-07 | agent | Backfilled round 4's answers: the panel can be widened; clicking lights up the full trail |
| V1.9 | 2026-09-07 | agent | Full review, 19 fixes: two numbering conflicts, two conflicts with existing decisions, phase prerequisites contradicting the body, and more |

## 1. Overview

- **Background**: right now in review, no panel shows how themes rotate or how they make their main run-up, just looking at theme strength it's hard to tell if a theme is a high-position theme or a low-position theme
- **Goal**: I need a new panel that can show how themes rotate and which are high-position vs low-position
- **Scope**: the web review home page + the operations admin console (the daily theme data page, entering a level per theme). The live-monitoring page and mobile are out of scope.
  > This line originally said "enter levels **and up/down moves**"; narrowed per 7.2-16: up/down moves can't be entered manually and are always computed by the algorithm.

- **Current-state baseline** (verified by the agent, 2026-09-07)

  | Item | Current state | What it means for this requirement |
  |:--- |:--- |:--- |
  | Bull/bear cycle band | Fully implemented: operations staff enter it daily, an existing panel already uses it, consecutive equal values merge into segments | Reuse as is, nothing new |
  | Theme daily % change | 🔴 The repo has **two** numbers both called "% change": one is float-cap weighted, the other is clearly distorted in certain special cases (from reading the code + production spot checks) | Must use the weighted one, with the definition fixed in the decisions |
  | Automatic theme-strength algorithm | Live, with configurable thresholds, full recompute, and manual values taking precedence | The ladder algorithm borrows its "shape" but can't reuse it directly (see 3.1.2) |
  | Daily theme list | After each trading day's close, it automatically inherits the previous day's theme list; production has accumulated over two months of data | Enough for the default range |
  | How continuously themes stay listed | 🔴 Only a handful of themes stay listed the whole time; the rest come and go (production data) | The biggest pitfall of "cumulative levels"; see 3.1.3 |
  | Admin theme row | One row already has several controls and is crowded horizontally | Adding "Level" means a redesign; do an admin prototype first |
  | Naming | Two panels already exist: "Limit-Up Streak Ladder" and "Live Limit-Up Streak Ladder" | The new panel's name must avoid confusion; see 7.2-20 |

---

## 2. Feature list

| Platform | Page | Feature | Description |
|:--- |:--- |:--- |:--- |
| Web | Review home page | Add a "Theme Ladder" panel | X axis is trading days, Y axis is theme level (levels 1–20 shown; level 0 = out, not shown); each cell shows the theme name, % change, and up/down/flat |
| Web | Theme Ladder | Bull/bear cycle band at the top | Reuses the existing band; consecutive equal values merge into segments |
| Web | Theme Ladder | Swipe left/right for earlier days | Default 60 trading days; swiping sends no requests |
| Web | Theme Ladder | Widenable panel, adaptive column count | Widening the panel shows more columns (5–16) |
| Web | Theme Ladder | Click a theme to light up its full trail | The same theme's cells on other dates light up together; the rest dim |
| Web | Theme Ladder | Hover popover | Theme name, % change, longest streak, streak distribution, limit-up count, limit-down count, tagged stocks |
| Web | Theme Ladder | Linked selection | Clicking broadcasts the selected theme |
| Admin | Daily theme data | Enter a level per theme | Integer 0–20, 0 = out. **This is the only way a theme enters** |
| Admin | Daily theme data | Theme row becomes a table layout | 7 controls aligned into columns; prototype first |

## 3. Functional requirements

### 3.1 Review: Add Theme Ladder panel

> The bracketed [ ] items and the ASCII sketch below are **the human's original text**: only one specific stock name was replaced with "a certain stock", and the rest is as written. This English edition translates them, so the original's punctuation and typos can't carry over; the tabs in the sketch are kept. The agent's additions start at 3.1.1.

[Panel name] Theme Ladder

[Panel layout]
1. bottom x axis shows dates
2. y axis is theme level
3. level 1 is lowest, going up 2, 3, 4, 5, 6 etc
4. top shows bull/bear cycle, take the market rhythm data from admin console

[Content]
1. show up, down, flat, or can also not show
2. show theme name and theme % change

[UI interaction]
1. mouse click and hover on a theme, show popover
2. popover content: theme name, % change, longest streak: a certain stock 3-day, 5-day streak 2 stocks, 3-day streak 1, 2-day streak 1, first limit-up 2, limit-up count, limit-down count, leader, catch-up, sentiment, etc tagged stocks
3. panel can swipe left right, show more content, default shows 90 days of content
4. for now no limit on level height, you can cap it at 20 levels in code

```
|-------------------------------------------------------|
|	bull cycle		|	bear cycle		  |		bull cycle			|
|				|				  |flat lvl3 Big Finance +3.21%	|
|				|down lvl2 Big Consumer	+4.21%|						|
|				|up lvl2 Agriculture  	+3.21%|						|
|lvl1 CPO	  +3.65%|				  |						|
|lvl1 PCB	  +4.53%|				  |						|
|-------------------------------------------------------|
|     9/1				9/2		  |			9/3			|
|-------------------------------------------------------|
```

[Data source]
1. add admin config, in daily theme data, support configuring level number and up/down number
2. also add an algorithm, rough core is, if a theme is up over 3% that day, then up a level, -3%~3% flat, -3% down a level. this algorithm can refer to the earlier weak-to-strong marker, you can suggest something more detailed.

[Panel type] snapshot panel

[Compatible global components]
1. share screenshot feature
2. VIP data display mechanism, follow global, same for all panels
3. singleton panel

#### 3.1.1 🔴 Core risk: a level is "cumulative state"

The original algorithm only says "up more than 3% today, go up a level", but not **up from which level**. Today's level = yesterday's level ± 1, so a level is a trail that accumulates over time, while every existing panel in the product "computes today from today"; there is no precedent. That raises questions the original didn't cover but that must be decided:

- What is the range of levels? Is the lowest 0 or 1? What does level 0 mean? (→ 7.2-1)
- Can the algorithm lower a theme all the way out? (→ 7.2-15)
- What can be changed manually: only the level, or up/down moves too? (→ 7.2-4, 7.2-16)
- If someone manually changes a level on one day, do later dates get recomputed? (→ 8-6. This one has no separate quote from the human; see the note on 8-6)

#### 3.1.2 Why not just use "N-day % change percentile"

The agent once proposed an alternative: compute a "position" directly from the percentile of the N-day cumulative % change, with no cumulative state. The human rejected it, on the grounds that there's no way to choose N and it can't reflect a theme's journey "from level 1 all the way up to level 5" (→ 7.2-5). **This rejection is what made the whole algorithm cumulative.**

#### 3.1.3 🔴 "Theme gaps" are the norm, not an edge case

The current-state baseline shows that nearly every theme is listed on and off. So "where does the level start when a theme disappears for a few days and comes back" is not an edge case but the main path, and it happens every day (→ 7.2-2).

#### 3.1.4 Empty and degraded states

| Situation | Behavior |
|:--- |:--- |
| No daily theme list for the review date | Empty state; keep the panel header and swipe controls; **do not fall back to the previous trading day** |
| Fewer days with a theme list than the visible range | Render the days that exist as normal; don't pad empty columns |
| A segment of the bull/bear cycle band not entered | Neutral gray segment (early on only a few days have values, so most of the band will be gray) |
| A theme not listed on some day | That column has no cell for it; no connecting line, no placeholder |
| Popover details loading | Skeleton screen; no bare "Loading" text |
| No leader tagged | The popover omits the leader row (tagging is purely manual, with no algorithmic fallback) |
| Just launched, nobody has marked any levels yet | The whole panel is empty (see 7.1-2); **this is expected** |

## 4. Non-functional requirements

> The original section listed technical requirements (how results are persisted, how the APIs are split, batch run time). Per the current template, only what users can see stays here; the technical content belongs in the spec's design.

| Item | This requirement |
|:--- |:--- |
| Refresh and timeliness | Computed once after the close each trading day, with a fallback recompute the next morning; after operations staff change a level, that theme's levels on later days update to match |
| Failure and restart | If the after-close computation fails, the next morning's fallback recompute fills the gap |
| Who can see it | Follows global permissions |
| Responsiveness | Swiping left/right and widening to change the column count send no requests and involve no waiting; popover details load on demand on hover |

## 5. UI/UX design

One prototype each for the user-facing site and the admin console, both with data at production scale: the user-facing prototype was checked in both the light and dark themes; the admin prototype is light only (the admin console has no dark mode).

Companion prototype: [prototype-theme-ladder-panel.html](prototype-theme-ladder-panel.html). It is a slimmed-down rebuild that follows this PRD's decisions; its data and stock names are fictional, the demo toggles at the top of the page map to item numbers, and it opens directly in a browser. The prototype surfaced three corrections to the PRD:

1. 🔴 The first user-facing prototype had only 12 themes, so the measured height came out too small; rebuilt at production scale, the panel is about 1745px tall. The original "no folding, no scrolling inside a level slot" (7.2-18) had to gain an exception (→ 7.2-24).
2. 🔴 No "next trading day" column is needed: unlike another panel that looks similar, the ladder carries no sense of "prediction".
3. Columns need stripes; without them you can't count by eye which column you're on.

## 6. Development phase plan

> The original numbered its phases A–H; in condensing, "read API" was folded into the user-facing panel, and the two prototypes are already done in §5, so the phases are renumbered 1–6 in release order.

| Phase | Scope | Releasable on its own? |
|:--- |:--- |:--- |
| 1 Data layer | Store levels and thresholds | ✅ Invisible to users; the developer self-verifies the data structures are ready |
| 2 Algorithm | Up/down moves and level accumulation, including edge cases like hitting the top, hitting the bottom, dropping off the list, and manual baselines | ✅ Invisible to users; dry-run against the last two months of production, and manually spot-check a few level trails |
| 3 Batch run and backfill | Daily computation + historical backfill | ✅ Invisible to users; read-only check in production that every theme has a result for every day. 🔴 **At this point every level should be 0**, because nobody has marked level 1 yet (7.2-2); don't mistake it for a bug |
| 4 Admin entry | The theme row becomes a table layout with a "Level" column; change one day and later days recompute | ✅ Operations staff change one day and see the later levels follow; **verify hands-on that drag-to-reorder still works** |
| 5 Cold-start entry | Operations staff give each currently listed theme an initial level | ✅ Done once operations staff finish the entry |
| 6 User-facing panel | The panel itself, band, swiping, widening, trail highlight, popover, linked selection | ✅ Eyeball check in both light and dark themes; screenshot sharing works; linked selection works |

🔴 **The user-facing panel deliberately comes after admin entry and cold-start entry.** A theme can enter only when operations staff mark it level 1 (7.2-2); without the admin entry point, the backfill is all level 0 and the panel launches empty.
> The previous version put the user-facing panel before admin entry, with its prerequisites listed only as "data API + prototype", contradicting this paragraph; corrected in the full review.

## 7. Confirmation items

### 7.1 For your information — items the agent flags for the human

- **7.1-1** The new panel's name is close to the existing "Limit-Up Streak Ladder" and "Live Limit-Up Streak Ladder", and the three will coexist for the long term.
- **7.1-2** A theme can enter only by being manually marked level 1, so on launch day the panel is bound to be empty until operations staff finish cold-start entry (phase 5).
- **7.1-3** Found by testing the prototype: clamping the algorithm's floor at level 1 makes levels drift upward over time. Logged as an item to watch.

### 7.2 Confirmed by the human

> Numbering rule: 7.2 and 7.3 share one increasing number range; a new item takes the current highest number + 1, and an item that moves between sections keeps its number.
> This rule exists because the two sections used to number separately, and twice the same number referred to different things; the numbers were fixed in the full review.

**Round 1 (14 items, excerpt)**

| # | Topic | Decision | In their words |
|:--- |:--- |:--- |:--- |
| 7.2-1 | Range of levels | 0–20; level 0 = out, not shown; the lowest shown is level 1 | "there is level 0, level 0 means out, not shown, lowest shown is level 1" |
| 7.2-2 | A theme returning after a gap | Dropping off the list resets it to level 0; to return, operations staff must mark it level 1 again; the algorithm only computes themes at level ≥1 | "go with A, dropping off resets to level 0, then can re-mark it as level 1. algorithm only computes themes level 1 and up" |
| 7.2-3 | Refining the algorithm | Phase 1 uses only the single ±3% threshold; none of the three enhancement suggestions | "accepted, phase 1 only uses % change" |
| 7.2-4 | What can be changed manually | Manual changes are to the level only; up/down is computed by the algorithm | "go with option A" |
| 7.2-5 | "Journey" or "position" | Journey (cumulative); the N-day percentile approach is rejected | "N-day change won't work, there's a problem, this N can't be picked, no way to reflect the theme's cycle, like going up from level 1 to level 5" |
| 7.2-8 | Vertical strategy | Render only the levels that have data; the panel grows taller with the data automatically | "pick 2" |
| 7.2-10 | Popover numbers | Switch with the global ST filter toggle (overturned the agent's suggestion) | "switch based on the ST toggle" |
| 7.2-14 | Default range | 60 trading days (originally 90); "under 10 columns per screen" was later relaxed by 7.2-25 | "90 days is too many, make the default 60 days, one screen should only show under 10 dates i think, i'll check when you draw the prototype" |

**Round 2 (4 items)**

> Round 2 raised 7 pending items, 15–21: this round answered 15, 17 and 20 and added a new one, 28; 16, 18 and 19 were not answered until round 3, and 21 is still open (see 7.3).

| # | Topic | Decision | In their words |
|:--- |:--- |:--- |:--- |
| 7.2-15 | Can the algorithm lower a theme to level 0? | No. The algorithm stops at level 1; out only manually, by operations staff | "algorithm can't lower a theme to level 0, only operations can lower it manually" |
| 7.2-17 | Click vs hover | Click = broadcast for linked selection; hover = popover only | "click becomes broadcast linking, hover shows popover" |
| 7.2-20 | Panel name | "Theme Ladder" | "just call the panel Theme Ladder" |
| 7.2-28 | How the admin side is built | Implemented per the agent's specific suggestion from the previous round (use the existing layout mechanism to get a table look, keeping drag-to-reorder) | "admin architecture as you suggested" |

> ⚠️ The words in 7.2-28 don't say which suggestion. The agent took them to mean that specific suggestion from the previous round, and writes this reading down here so it isn't later taken to mean something else.

**Round 3 (3 items)**

| # | Topic | Decision | In their words |
|:--- |:--- |:--- |:--- |
| 7.2-16 | Restore the original's "support configuring up/down numbers"? | No: manual configuration is the level only, and up/down is computed by the algorithm; narrowing that half-sentence of the original is confirmed | "support configuring level, up/down by the algorithm" |
| 7.2-18 | How to order themes at the same level | Stacked vertically (no folding, no scrolling inside a level slot), sorted by that day's gain, descending; ties go by operations staff's ordering | "same-level themes, sort by gain, stack in a column" |
| 7.2-19 | Does the level follow the ST toggle? | No; only the counts in the popover do | "level doesn't follow ST" |

**Round 4 (second prototype iteration, 4 items)**

| # | Topic | Decision | In their words |
|:--- |:--- |:--- |:--- |
| 7.2-24 | What to do about the panel being too tall | Fixed panel height, with the cell area scrolling vertically; 7.2-18 gains one exception: panel-level scrolling is allowed, while scrolling inside a slot and folding remain banned | "prototype, go with the option you recommend" |
| 7.2-25 | Panel width | Can be widened; the column count adapts to the width, 5–16 columns; seeing all 60 days is done by swiping, not widening | "need to support widening the panel, can show more columns" |
| 7.2-26 | Trail highlight | Click a theme → that theme's full trail lights up + the rest dim + auto-scroll to the trail + click again to cancel | "click a theme, then this theme's positions on other dates also need to light up together" |
| 7.2-27 | Position of the admin level column | Right after the theme name, to the left of the original first column | "put level to the left of a certain column" (field name replaced) |


### 7.3 Pending the human's confirmation

> None of the remaining 4 items blocks starting work. Their numbers share a range with 7.2, so none collides with any item above.

- **7.3-21** 🟡 Should the panel accept selected themes broadcast by other panels? Now that 7.2-26's trail highlight has landed, the implementation cost is much lower, so it's worth another look.
- **7.3-22** 🟡 One color in the bull/bear cycle band fails the contrast requirement in the dark theme, and it also affects another panel already live: change the color in the data, or override it in the front end?
- **7.3-23** 🟡 The green text for declines in flat cells has a contrast ratio of only 3.30:1. This is a site-wide issue: should it become a project of its own?
- **7.3-29** 🟡 After operations staff change a level, should the admin console show "recomputed N trading days"? Suggestion: no. Save silently after the change; the recompute finishes in the same request, so operations staff notice no difference, and a loading state would slow down high-frequency entry.

## 8. Decision digest (for whoever writes the spec)

- **8-1** Panel name "Theme Ladder"; a snapshot panel, singleton. (Source: 7.2-20, §3.1)
- **8-2** Levels 0–20; 0 = out, not shown; 1–20 shown. (7.2-1)
- **8-3** A theme enters only when operations staff manually mark it ≥1; the algorithm never lets a level-0 theme in. (7.2-2)
- **8-4** Out only manually (mark it 0, or delete it from that day's theme list → dropping off resets it to 0); the algorithm stops at level 1. (7.2-15)
- **8-5** Up/down: daily weighted % change ≥ +3% is up, ≤ −3% is down, in between is flat; phase 1 uses only % change. (7.2-3, §1 current-state baseline)
- **8-6** Manual changes are to the level only; the manual value becomes the new baseline, and that theme's later trading days are recomputed in date order. (7.2-4, 7.2-16. ⚠️ "Recompute later days" has no separate quote from the human: the agent proposed it in the definitions and it was confirmed together with the whole set of definitions in round 1. By the rules it should have been a confirmation item of its own; this is a gap in this case study)
- **8-7** Default 60 trading days, swiping sends no requests; seeing all 60 days is done by swiping, not widening. (7.2-14, 7.2-25)
- **8-8** The column count adapts to the width, 5–16 columns. (7.2-25)
- **8-9** The Y axis renders only levels that have data; the cell area scrolls vertically at the panel level. (7.2-8, 7.2-24)
- **8-10** Same-level themes stack vertically, sorted by that day's gain, descending; ties go by operations staff's ordering. (7.2-18)
- **8-11** Click = broadcast for linked selection + light up the full trail; hover = popover. (7.2-17, 7.2-26)
- **8-12** The ST toggle affects only the counts in the popover; level and % change don't follow it. (7.2-10, 7.2-19)
- **8-13** The bull/bear cycle band reuses the existing implementation; no future columns are drawn. (§1 current-state baseline, §5)
- **8-14** Launch order: data layer → algorithm → backfill (all 0 is normal) → admin entry → cold-start entry → user-facing panel. (§6)

---

## Appendix: What it looks like as a spec

The spec's requirements are rewritten from §8, each with its source marked, not copied wholesale. Below is an **illustration**: two Tier C `requirements.md` entries rewritten from this PRD's decisions, not the original spec text.

> **R3 Theme entry**
> **Human's words / source**: PRD `PRD-review-add-theme-ladder-panel.md`, decisions 8-3, 8-4.
> A theme can enter only when operations staff mark it ≥1 in the admin console; the algorithm never raises a level-0 theme to level 1, and never lowers a theme at ≥1 to level 0.
> - AC3.1: A theme not manually marked today, at level 0 the previous day, gains +8% today → still level 0 today, not shown on the panel.
> - AC3.2: A theme at level 1 the previous day falls −6% today → still level 1 today (at the floor), not out.
> - AC3.3: Operations staff mark a theme 0 on some day → the theme is not shown on that day or any later day until it is marked ≥1 again.
>
> **R6 Propagation of manual level changes**
> **Human's words / source**: decision 8-6.
> After operations staff change a theme's level on one day, that theme's level on every later trading day is recomputed in date order, with the changed value as the new baseline; other themes are unaffected.
> - AC6.1: Change a theme on 9/2 from level 3 to level 5, and 9/3 gains +4% → 9/3 shows level 6.
> - AC6.2: Before and after the same operation, every other theme's level on every date is unchanged.

Note three things: references to the PRD give only the file name, not the directory (the PRD is archived once done, and a path with a directory breaks as soon as it's archived); acceptance criteria are written as inputs and outputs that can be judged right or wrong; technical design that isn't in the PRD goes into `design.md` later.

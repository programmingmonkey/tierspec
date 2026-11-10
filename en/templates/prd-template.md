# PRD-<platform>-<one-line requirement name>

<!--
TierSpec PRD template. Recommended for Tier C product requirements (user-visible behavior is changing), and especially for new modules and new pages. For how to use it, see Chapter 6, "From PRD to Spec".

Who fills in what:
- The human writes: the Background / Goal / Scope in §1, the feature list in §2, and the [ ] fields under each feature in §3. Leave blank anything you can't write; the agent will follow up in §7.3.
- The agent completes the remaining sections. The agent doesn't change the human's original text; additions and ambiguities go below the original text, numbered from 3.x.1, each pointing to a number in §7.

Each row of the version table gets one sentence only (what this version changed); details go in the body or in §7. Write dates with their time zone.
This template is released under the MIT license (see LICENSE-CODE in the repo). Once you copy it into your project you can change it freely, and this comment block can be deleted.
-->

| Doc version | Revision date | Revised by | Changes          |
|:----------- |:------------- |:---------- |:---------------- |
| V1.0        | YYYY-MM-DD    | Human      | Document created |

## 1. Overview

- **Background**: What doesn't work well now, and who is affected, in what situation.

- **Goal**: Once this is done, what users can do that they can't do now.

- **Scope**: Which platforms (Web / mobile / admin console / server …) and which pages are involved.

- **Current-state baseline** (filled in by the agent): the current state as verified during discussion, each item marked with its source and date, in two parts: "from reading code" and "from production data".
  Data conclusions (how many rows, what values, whether such data exists at all) must be checked in production, not locally.
  It is only a basis for discussion; when the spec is written, it still has to be registered and verified again.

  | Item | Current state (source, date) | What it means for this requirement |
  |:---- |:---------------------------- |:---------------------------------- |
  |      |                              |                                    |

---

## 2. Feature list

| Platform | Page | Feature title | Feature description |
|:-------- |:---- |:------------- |:------------------- |
|          |      |               | One sentence        |

## 3. Functional requirements

### 3.1 <feature name>

[Name]

[Layout] ASCII art is fine; mark what goes in each area.

```
|----------------------------------------|
| <title row>                            |
| <area A>            | <area B>         |
|----------------------------------------|
```

[Legend] What each character, symbol, and number in the layout diagram means (anything you leave out, the agent can only guess).

| On the diagram | Meaning |
|:-------------- |:------- |
|                |         |

[Content and data logic]
1.

[Definitions] Every number and every label on the screen must be able to answer the columns below; write "?" where you're unsure, and the agent will look up the existing definitions.

| Metric / label | Meaning | Scope (which special cases are included or excluded) | As of when (real-time / snapshot at a set time / computed after the fact) | Same definition as which existing feature |
|:-------------- |:------- |:---------------------------------------------------- |:------------------------------------------------------------------------- |:----------------------------------------- |
|                |         |                                                      |                                                                           |                                           |

[Relationship to existing features / concepts]
- Does the product have any concept with **the same name but a different meaning**? What does it mean elsewhere?
- Which existing feature's definition or data does this reuse? Which numbers in this feature must match up with which place?

[Data volume and overflow]
- At most how many items / columns? (the agent will give the daily average, median, and maximum from production data)
- What happens when it doesn't fit horizontally or vertically (pagination / scrolling / show only the top N)?
- What is shown when there are 0 items?

[Time periods and states] For each row write "what is shown"; write "N/A" where it doesn't apply. Rename the rows to fit your business.

| State | What is shown |
|:----- |:------------- |
| Data not ready |  |
| Partially ready |  |
| Historical date |  |
| Non-business day (holidays, service outages, etc.) |  |
| Dates before launch, with no data |  |
| Loading |  |
| No data |  |
| Request failed / upstream computation failed |  |

[Interaction between manual operations and the algorithm] (fill in only if there is an operations entry point)
- What can operations staff change? Which dates does a change affect (that day only / the days after / earlier days too)?
- Can the algorithm overwrite manual values? How are multiple manual operations combined when they stack up?

[Compatibility with global capabilities] Every row must be answered; write "N/A" where it doesn't apply. Add or remove rows to match the global capabilities your product already has.

| Global capability | This feature |
|:----------------- |:------------ |
| Permissions / paywall | Follows global / has its own requirements |
| Sharing, screenshots | Which controls stay out of the shot? When content overflows, which part is captured? |
| Filter toggles | Does it follow the global filters? Which numbers follow and which don't? |
| Linked selection | What it broadcasts, what it consumes |
| Click behavior | What clicking each kind of element does |
| Sorting | Sort rule + how ties are ordered |
| Refresh and reset | How often it refreshes; what is cleared and what is kept when the day rolls over |
| Privacy masking | Does it show anything that needs masking? |

## 4. Non-functional requirements

> Write only behavior that **users can see and that can be checked at acceptance**. Technical design (tech stack, tables, APIs, caching, scheduled jobs) always goes in the spec's design, never in this document.
> Technical constraints the agent finds during discussion: those that affect product trade-offs go in §7.1 (For your information) or §7.3 (Pending), phrased as "the cost is that users will see X"; those that don't are left out.
> Any technical numbers in this document are only suggestions; the spec's design is authoritative.

| Item | This requirement (write "N/A" if it doesn't apply) |
|:---- |:-------------------------------------------------- |
| Refresh and freshness | How often it updates; the latest time the data is ready |
| Failures and restarts | What users see when the service restarts or upstream data is missing or late; what must not be lost |
| Who can see it | Public / logged in / paid; who the admin console entry point is for |
| Response speed | The wait users will accept (e.g. content within 1 second of opening) |

## 5. UI/UX design

> New screens get a prototype first, and the prototype is the visual source of truth; sizes, column widths, and minimum widths and heights are as measured in the prototype.
> Run the prototype at real data scale: it often overturns assumptions in the body, and when it does, go back to §7 and decide again.

Prototype path:

## 6. Development phase plan

> 🔴 If you can't write a phase that "can be released independently", it isn't a phase: either merge it into an adjacent phase or slice it again.
> The third column doesn't accept adjectives like "basically done" or "mostly usable"; it must answer "who verifies, and what".
> Anything that depends on another requirement not yet shipped or not yet accepted gets its own "Prerequisite" row.
> The spec turns this table into its phasing table; if it needs splitting into several specs, write the split and the release order into the topic README (the overview in the topic directory; see Chapter 5).

| Phase | Scope (features) | Independently releasable? |
|:----- |:---------------- |:------------------------- |
| Phase 1 | | ✅ / ❌ + who verifies, and what |
| Phase 2 | | |

## 7. Confirmation items

> 7.2 and 7.3 share one increasing number sequence (7.1 has its own): every new item takes "current highest number + 1", and keeps its number when it moves from 7.3 to 7.2.
> Without this, sooner or later the same number will point to different things, while the body is full of "see 7.2-N" cross-references.
> Once something is decided, backfill the body; here keep only the number, a one-sentence conclusion, and the human's own words.

### 7.1 For your information (items the agent flags for the human)

> Things the human needs to know but doesn't need to decide: an upstream dependency that hasn't been accepted, a definition that doesn't match an existing feature, a user-visible cost of a technical constraint.

### 7.2 Confirmed by the human

> When the human's words are only an option code ("go with A", "option 2"), the Decision column must spell out the chosen option in full.

| # | Topic | Decision | In their words |
|:- |:----- |:-------- |:-------------- |
| 7.2-1 | | | "" |

### 7.3 Pending the human's confirmation

> Mark each item 🔴 (blocking: without a decision there can be no prototype or spec) or 🟡 (has a default suggestion); when the agent makes a suggestion, label it "Suggestion".
> The human replies on a new line beneath the item with `Answer: …`; for 🟡 they can reply just "as suggested". In the next version, the agent moves the reply into 7.2 and backfills the body.

## 8. Decision digest (for whoever writes the spec)

> Number every item; each is a one-sentence decision + its source (a § of the body, or 7.2-N).
> The spec's requirements are rewritten from here, each item marked with its source, not copied over wholesale; on conflict the spec wins, and this document gets corrected afterwards.

- 8-1: <one-sentence decision> (source: §3.1 / 7.2-1)

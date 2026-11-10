# Chapter 0 · Grown from Fupanbao

None of TierSpec's rules were designed up front. Each one was forced out of a real project by a real problem. That project is called **Fupanbao** (复盘宝, roughly "review treasure").

🔗 **https://fupanbao.top**

## What it is

Fupanbao is a daily post-market review and live market dashboard for China's A-share market: limit-up streak ladders, the Dragon-Tiger List (the exchanges' daily disclosure of top traders), theme sectors, "market weather", and candlestick and intraday charts for individual stocks. It helps investors review the day systematically after the close and follow live moves during the session. There is also a writing pipeline: after the close, send one message in Feishu (Lark) and it generates that day's review article.

It was written from scratch, deployed and operated by one person plus AI: a pnpm monorepo with a user-facing app, an admin console, an API service (Fastify + Prisma + PostgreSQL) and a Python market-data collector, running on a cloud server.

## Why this project could force a set of rules

- **Time is a hard constraint.** Trading days, the call auction, intraday, after the close: the data you should see differs at each point in time, and everything runs on Beijing time. Get the time wrong in one place and a whole swath of data goes wrong.
- **Wrong data is just wrong.** An endpoint returning 200 and a page with no errors don't mean the data is right. AI is all too ready to "verify" a wrong result as passing.
- **Nothing may break during trading hours.** Deploys, data fixes and collector changes all have to avoid the trading session, and all have to be reversible.
- **One person maintains several apps.** No colleague reviews your work, so the process and machine gates have to act as the second pair of eyes.

## How the rule system grew

| When | What grew | Problem it solved | Chapter |
|---|---|---|---|
| 2026-04 | Project starts | — | — |
| 2026-06 | The first git hook | Block force-pushes to and deletion of the main branch | 2 |
| 2026-07 | Epistemic honesty rules | The agent wrapped a batch of untrustworthy data into a conclusion, then a document, then a retrospective; each step looked more polished, and the error never changed | 11 |
| 2026-08 | Rules delivered by file path | The always-on entry file has a length cap, and the backend conventions and design spec most often tripped over during tasks never reached the agent at all. The first version was a mirror synced from elsewhere; a week later it was deleted wholesale because the copies drifted (Chapter 4). It was rebuilt in 2026-09 with the content written directly in the rule files | 3, 4 |
| 2026-08 | Deploy gates moved into the script | While hooking up a new tool that couldn't read the rules, it turned out the three deploy gates had not a single line of implementation in the deploy script | 2 |
| 2026-08 | Guardrails must carry self-tests | A format checker silently stopped working four separate times, with no signal any of those times | 2 |
| 2026-08 | Code from local, data from production | On one day the local database was used as evidence for data three times; once, a whole fallback path was designed around an empty table | 11 |
| 2026-09 | Action gates (read before you act) | Before the first commit or deploy, the matching rules must be read in full, not recalled from memory | 3 |
| 2026-09 | New spec system | The old spec had bloated to 37KB and nobody could read it all; it was rewritten as a lean version (about 7KB) that depends on no particular tool and that any agent can follow by reading plain markdown, plus a lint that checks structure only | 5 |
| 2026-11 | Engineering contracts | Engineering behavior rules had been mixed into the visual design spec; they were split out, each with a registered machine guard | 9 |

A snapshot as of 2026-11-10 (not live data): about 7,600 commits, of which about 720 changed the toolchain itself (counted by these paths: the entry file, rules, skills, subagent config, hook wiring and scripts, git hooks, the rule-reading script, spec and doc conventions, engineering contracts, and the master design spec); 37 spec topics completed; 42 engineering contracts registered.

## How to read this book

Read Chapter 1 first to see which layer of Claude Code each of these rules lives in; after that, each chapter covers one class of problem. Every rule comes with the problem that forced it. Tailoring rules by their criteria beats copying them: first check whether your project has the same problem, then decide whether you need the rule.

Fupanbao's source code is not open; this repository covers only the method.

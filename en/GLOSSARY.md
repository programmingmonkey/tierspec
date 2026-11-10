# Glossary (中文 → English)

Every English term used for TierSpec's core ideas, fixed once so the whole English edition says the same thing the same way. The left column is the term as it appears in the Chinese edition.

## Core workflow

| 中文 | English | Notes |
|---|---|---|
| 分档式 AI 工程规范 | tiered AI engineering practice | The book's subtitle |
| 定档 | tiering | Verb: "tier the change", "decide the tier" |
| 档位 | tier | |
| A / B / C 档 | Tier A / B / C | |
| A 直接改 | Tier A: change directly | |
| B 轻量计划 | Tier B: lightweight plan | |
| C 完整 | Tier C: full process | |
| 只读调研 | read-only investigation | |
| 报四行 | the four-line report | Its lines: Root cause (or Goal) / Impact / Similar cases / Fix |
| 根因 / 目标 | Root cause / Goal | |
| 影响面 | Impact | In running prose too: "the impact", not "blast radius" |
| 同类 | Similar cases | |
| 改法 / 修法 | Fix | "Fix" means the change to make, whatever the change type |
| 一句话说清 | can be stated in one sentence | |
| 撤不回 | irreversible / can't be undone | |
| 拍板 | (the human) decides / signs off | |
| 风险加码 | risk add-ons | |
| 风险不定档，只加码 | risk doesn't set the tier, it only adds requirements | |
| 必问名单 | must-ask list | |
| 产品需求 / 技术改造 / 缺陷修复 / 工程任务 | product requirement / technical rework / bug fix / engineering task | |
| 研发体系 | the development system (tools, rules, CI, scripts, agent config) | |
| 负对照 | negative control | |
| 执行中复核 | mid-execution re-check | |
| 完工验收 | completion check | |
| 验收 / 验收标准 | acceptance criteria | A single one: "acceptance criterion" |
| 验证 | Verification (as a task field); verify | |
| 存量 | existing / legacy (code, specs) | |
| 起步的最小组合 | the minimal starting set | |

## Spec structure

| 中文 | English |
|---|---|
| spec | spec |
| 主题目录 / 主题 README | topic directory / topic README |
| 状态：草稿 → 已批准 → 执行中 → 已完成；已搁置 | Status: Draft → Approved → In progress → Done; Shelved |
| B 档 spec.md 三节：目标与不做 / 做法与步骤 / 记录 | Goals and non-goals / Approach and steps / Log |
| 不做什么 | non-goal ("what we won't do") |
| 待确认 | open questions (in a spec); Pending (as a PRD section) |
| requirements.md：背景与目标 · 范围 · 验收标准 | Background and goals · Scope · Acceptance criteria |
| design.md：现状与方案 · 分期表 | Current state and approach · phasing table |
| tasks.md：任务 · 记录 | Tasks · Log |
| 记录节 | the Log section |
| 新增 / 修改 / 废止 | Added / Modified / Removed |
| 变更快照 | change snapshot |

## PRD

| 中文 | English | Notes |
|---|---|---|
| PRD / 产品需求文档 | PRD / product requirements document | |
| 原型 | prototype | |
| 原始需求 | original requirement (the human's raw write-up) | |
| 现状基线 | current-state baseline | |
| 口径 | definition (of a number or label: what it means, as of when, matching which panel) | "改数据口径或统计口径" → "change a data or metric definition" |
| 口径表 | definitions table | |
| 确认事项 | confirmation items | |
| 告知 / 已确认 / 待确认（三栏） | For your information / Confirmed / Pending (three sections) | PRD §7.1 / 7.2 / 7.3 |
| 原话 / 人的原话 | the human's own words / "In their words" (column) | |
| 定案 | decision | |
| 定案速查 | decision digest | PRD §8 |
| 阶段规划 / 阶段表 | phase plan / phase table | |
| 前置 | prerequisite | |
| 演示开关 | demo toggles | |
| 按建议 | "as suggested" | Shorthand reply to a 🟡 item |
| 答：… | Answer: … | How the human replies under an item |
| 同名不同义 | same name, different meaning | |

## Rule delivery and enforcement

| 中文 | English |
|---|---|
| 规则 / 规矩 | rule |
| 文字规则 | written rules |
| 机器门槛 | machine gates |
| 硬门槛 | hard gates |
| 门槛 | gate |
| 护栏 | guardrail |
| 守卫 / 机器守卫 | guard / machine guard |
| 自测 | self-test |
| 影子期 | shadow period |
| 先读后做 | read-before-act gate (the practice: "read before you act") |
| 动作门槛 | action gate |
| 送达 / 通道 | delivery / channel |
| 开场常驻 / 常驻规则 | always-on at session start / always-on rules |
| 按路径送达 / 按路径规则 | path-scoped delivery / path-scoped rules |
| 按需调用 | on-demand invocation |
| 入口文件 | entry file |
| 触发表 / 动作触发表 | trigger table / action trigger table |
| 读规则脚本 | rule-reading script |
| 头标 / 尾标 | header marker / footer marker |
| 大文件按章读 | read large files section by section |
| 输出上限 / 超限提示 | output cap / over-the-cap notice |
| 判定器 | checker (of a gate or hook) |
| 映射守卫 / 映射与加载链 | mapping guard / the mapping and the loading chain |
| 压缩（会话） | compaction (of a session) |
| 唯一真源 | single source of truth |
| 指路 | point to it (a pointer, not a copy) |
| 副本漂移 | the copies drift (drift) |
| 改三漏一 | "changed three, missed one" |
| 现测 | check live (state how to measure it now, not the number) |
| 增删门槛 | the bar for adding and removing rules |

## Claude Code layers

| 中文 | English |
|---|---|
| 工具分层 | tool layers |
| 内容层 / 文字层 / 配置层 | content layer / text layer / configuration layer |
| 技能 | skill |
| 项目技能 / 用户级技能 | project skills / user-level skills |
| 子代理 | subagent |
| 主会话 | main session |
| 记忆 | memory |
| git 钩子 | git hooks |
| Claude hooks / hook | Claude hooks / hook |
| 放行 | allow (a permission rule); let through (a gate) |
| 入库 / 不入库 | committed / not committed (to the repo) |
| 主工作区 | main worktree |
| 代码定位 / 代码追踪 / 资料调研 / 审查 / 执行 | code locator / code tracer / researcher / reviewer / executor |
| 模型档位：最小档 / 中档 / 最强档 | model tier: smallest / mid / strongest |

## Review

| 中文 | English |
|---|---|
| 审查 | review |
| 两路独立审查 | two independent reviews (two review tracks) |
| 写作者自查 | author self-check |
| 审查员 | reviewer |
| 需求审查 / 代码审查 / 设计评审 | requirements review / code review / design review |
| 样本集 | sample set |
| 召回 / 命中 | recall / hits |
| 整体审查 | full review |
| 路（一路审查） | track (a review track) |
| 命令行一路 / 子代理一路 | CLI track / subagent track |
| 真问题 / 不必改 / 判不了 | real issue / no change needed / can't tell |
| 降级声明 | degradation statement |

## Living docs and contracts

| 中文 | English |
|---|---|
| 活文档 | living docs |
| 文档地图 | doc map |
| 过程文档 | process docs |
| 事故记录 | incident records |
| 生成物 | generated artifacts |
| 部署手册 | deployment runbook |
| 权威源 | authoritative source |
| 工程契约 | engineering contracts |
| 不变量 | invariant |
| 仅文字 | "text only" (a contract with no machine guard) |
| 例外登记 | exception register |
| 索引 | index |
| 生成块 | generated block |
| 守卫路由 | guard routes |
| 文档同步表 | doc sync table |

## UI design system

| 中文 | English |
|---|---|
| 设计体系 | design system |
| 设计主规范 / 主规范 | master design spec ("master spec" for short, after first use) |
| 视觉语言 | visual language |
| 设计令牌 / 令牌 | design tokens / tokens |
| 令牌准入 | token admission |
| 轴表 / 轴 | axis table / axis |
| 定死 / 发挥 | fixed / free |
| 四种模式 | four modes |
| 红线 / 风格原则 | red lines / style principles |
| 上游 / 锁版本（LOCK） | upstream / version lock (LOCK) |
| 盲选 | blind comparison |

## Epistemic honesty and production

| 中文 | English |
|---|---|
| 认识诚实 | epistemic honesty |
| 守则 | guideline |
| 事实性陈述 | factual claim |
| 查线上 / 线上 | check production / production |
| 本地库 | local database |
| 只读通道 / 只读账号 | read-only channel / read-only account |
| 来源标注〔事实〕〔推断〕〔猜测〕〔工具返回〕 | source tags [fact] [inference] [guess] [tool output] |
| 〔项目主人原话〕〔项目主人的理由，转述〕 | [owner's words] [owner's reasoning, paraphrased] |
| 生产操作纪律 | production operations discipline |
| 写线上数据 | write production data |
| 口令（人的确认） | confirmation phrase |
| 口令（凭据） | password |
| 快照 | snapshot |
| 对账 / 独立对账 | reconciliation / independent reconciliation |
| 演练 | dry run (rehearsal) |
| 业务高峰窗口 | business peak window |
| 线上验证待办 | production verification to-dos |

## Chapter section headings

| 中文 | English |
|---|---|
| 第 N 章 | Chapter N |
| 遇到的问题 | The problem |
| 理念 | The idea |
| 怎么落地 | In practice |
| 代价与适用条件 | Costs and when it applies |
| 踩过的坑 | Pitfalls we hit |
| 依据与对照 | Sources and comparisons |

## People

| 中文 | English | Notes |
|---|---|---|
| 人 | the human | As opposed to the agent |
| 作者项目 | the author's project | |
| 项目主人 | the project owner | |
| 运营 | operations staff | In the case study |
| 复盘宝 | Fupanbao | Named only in Chapter 0, the README and the case study's intro note, as in the Chinese edition |

## A-share market terms (case study and prototype)

Chinese A-shares have a daily price limit (usually ±10%); hitting it is a "limit-up" or "limit-down".

| 中文 | English | Notes |
|---|---|---|
| A 股 | China's A-share market | |
| 复盘 | post-market review ("review" in page names) | |
| 盯盘 | live monitoring | |
| 盘中 / 盘后 / 竞价 | intraday / after the close / the call auction | |
| 交易日 | trading day | |
| 北京时间 | Beijing time | |
| 红涨绿跌 | red for up, green for down (the Chinese market convention) | |
| 题材 | theme (a market theme or concept stocks trade on) | |
| 题材天梯 | Theme Ladder (panel name) | |
| 连板天梯 / 实时连板天梯 | Limit-Up Streak Ladder / Live Limit-Up Streak Ladder | |
| 等级 | level | |
| 升级 / 降级 / 平级 | up / down / flat (a level) | |
| 出局 | out (level 0, not shown) | |
| 在档 / 断档 / 建档 | listed / dropped off the list / daily theme list | |
| 涨停 / 跌停 | limit-up / limit-down | |
| 连板 / N 连板 / 首板 / 最高连板 | consecutive limit-ups / N-day limit-up streak / first limit-up / longest streak | |
| 龙头 / 补涨 / 情绪 | leader / catch-up / sentiment | Tags put on individual stocks: the stock leading a theme; a laggard catching up with the theme; a stock driven by market sentiment |
| 主升 | main run-up | The main upward leg of a theme's cycle |
| 高位题材 / 低位题材 | high-position theme / low-position theme | A theme that has already run up a long way (late in its cycle) / one still early in its run |
| 龙虎榜 | Dragon-Tiger List (exchange disclosure of top traders) | |
| 涨跌幅 | % change | |
| 流通市值加权 | float-cap weighted | |
| 多空循环 | bull/bear cycle | |
| 大盘节奏 | market rhythm | |
| 大盘天气 | market weather | |
| 弱转强 | weak-to-strong | |
| 横条 | band (the bull/bear cycle band) | |
| 轨迹 | trail (a theme's level trail) | |
| 标级 | mark (a theme) level N | |
| ST 筛选开关 | ST filter toggle (ST = "special treatment" stocks flagged for risk) | |
| 快照面板 / 单例面板 | snapshot panel / singleton panel | |
| 浮窗 | popover | |
| 联动 / 广播 | linked selection / broadcast | |
| 后台 / 前台 | admin console / user-facing site | |

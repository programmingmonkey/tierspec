# 第 2 章 · 规则怎么送达 agent

## 遇到的问题

规则写好了，agent 却照样犯规则里写着的错。复盘下来，多数时候不是它不听话，而是**那一刻规则根本不在它的上下文里**：

- 所有规则都塞进 `CLAUDE.md`，越写越长，每条被遵守的概率越来越低，最后不得不删；
- 规则放在单独的文件里，但 agent 不知道该去读，或者知道但没读；
- 读了，可文件太大，工具只把开头一小段放进上下文，其余被悄悄截掉；
- 会话被压缩，开场读过的规则跟着丢了。

## 理念

**规则不是写在仓库里就算数，要设计它「什么时候、通过哪条通道」进入 agent 的上下文。**

不同的规则需要不同的送达时机。按「什么时候需要」分成四条通道：

| 通道 | 什么时候进上下文 | 放什么 | Claude Code 里的落点 |
|---|---|---|---|
| **开场常驻** | 每个会话一开始；压缩后自动重载 | 每个会话都要用的：项目总览、红线、语言与时间约定、敏感数据守则 | `CLAUDE.md` + `.claude/rules/` 下不带 `paths:` 的文件 |
| **按路径送达** | 读写匹配某些路径的文件时 | 只在碰某类文件时才用的：后端约定、设计规范索引、文档库规则 | `.claude/rules/` 下带 `paths:` 的文件 |
| **动作前先读后做** | 第一次要执行某类动作之前 | 撤不回的动作的完整流程：提交与推送、部署、改生产数据 | `PreToolUse` hook 拦下，要求先整份读完 |
| **按需调用** | agent 判断需要，或用户点名 | 多步流程：写 spec、审查、查线上数据、做 UI | `.claude/skills/` |

另有第五类不靠送达的：**必须成立的事，不放在任何一条通道里，放进机器门槛**（第 1 章）。

### 每条通道的取舍

- **开场常驻要少而硬。** 它占的是每个会话的上下文。只放事实、红线和「去哪找」的指路，不放流程细节。给它设一个总量上限，并用脚本守住。
- **按路径送达最省，但触发条件容易误判**（见下文「踩过的坑」）。
- **动作门槛最可靠，但有摩擦。** 只给少数「做错了撤不回」的动作用。
- **技能按需调用，最灵活，也最依赖 agent 自觉。** 技能的描述写清「什么时候用、什么时候不用」，在入口文件里再列一张「要做的事 → 先跑哪个技能」的触发表。

## 怎么落地

### 入口文件只做地图

`CLAUDE.md` 不写规则正文，只写三件事：规则有哪几条送达路径、每类动作之前先读什么（触发表）、大文件怎么读。例如下面这张触发表。

> 说明：本书示例里的 `scripts/read-rules.sh`（读规则脚本）和 `/spec`、`/design-ui`、`/db-readonly` 这几个斜杠命令，都是**你需要在自己项目里自建**的脚本和技能，不是 Claude Code 内置的，本仓库也不提供。`read-rules.sh` 做的事很简单：按名字（topic）输出对应规则文件的全文，在首尾各打一行 `# topic: <名>`、`# end-of-topic: <名>` 标记；另支持 `--toc` 列目录、`--section` 取单节（见下文「大文件按章读」）。

```markdown
## 动手前先取：动作触发点

| 要做的事 | 先跑 |
|---|---|
| 提交 / 合并 / 推送 / 建分支 | `bash scripts/read-rules.sh git`（有门槛：没读过就提交会被拦下） |
| 部署 / ssh 上服务器 | `bash scripts/read-rules.sh deploy`（同上） |
| 改代码、规则、脚本的行为之前 | `/spec` 第 1–3 步：只读调研 → 报四行 → 推荐档位 |
| 改界面 | `/design-ui` |
| 查线上数据做结论 | `/db-readonly`（只读） |
```

### 按路径规则：一份规则，一组路径

```markdown
---
paths:
  - "server/**"
  - "shared/**"
---

# 后端约定

- 时间列一律存带时区的类型；……
```

经验上，一份按路径规则最好只管一类文件，正文只放「碰这类文件时最容易犯、而且读代码看不出来」的几条。完整说明放活文档，规则里只写指路。

### 先读后做：动作门槛

这是介于文字规则和硬门槛之间的一层（第 1 章）：它保证 agent 动手前，对应的规则在上下文里；不保证它照做，也不是授权证明。用 Claude Code 的 hook 实现：

1. `PreToolUse`：判断即将执行的命令属于哪类动作（提交、推送、部署、写生产库……）。本会话还没读过对应规则的，拒绝执行，并提示先跑哪条读规则的命令。
2. `PostToolUse`：确认读规则的那条命令**整份读完了**。判据是输出里头标、尾标都在；`| head` 这类只读一部分的不算。确认后记下「本会话已读」。
3. `SessionStart`：会话被压缩或清空时，读过的规则已经不在上下文里，标记作废，要重读。

#### 最小实现

`.claude/settings.json` 里接三个 hook：

```json
{
  "hooks": {
    "PreToolUse":  [{ "matcher": "Bash", "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/scripts/hooks/read-gate.py\" pre" }] }],
    "PostToolUse": [{ "matcher": "Bash", "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/scripts/hooks/read-gate.py\" post" }] }],
    "SessionStart": [{ "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/scripts/hooks/read-gate.py\" start" }] }]
  }
}
```

`scripts/hooks/read-gate.py`：

```python
#!/usr/bin/env python3
"""先读后做：本会话第一次提交 / 推送 / 合并之前，必须整份读完 git 规则。"""
import json, os, re, sys

def main():
    mode = sys.argv[1]                      # pre | post | start
    d = json.load(sys.stdin)
    sid = re.sub(r'[^A-Za-z0-9_-]', '', d.get('session_id', ''))[:64]
    if not sid:
        return                              # 取不到会话就放行：门槛坏了不能把人锁死
    state = os.path.join(os.environ.get('CLAUDE_PROJECT_DIR', '.'), '.claude', 'read-gate')
    os.makedirs(state, exist_ok=True)
    mark = os.path.join(state, sid + '.git')
    cmd = (d.get('tool_input') or {}).get('command', '')

    if mode == 'start':                     # 压缩或清空上下文后，读过的规则不在了，标记作废
        if d.get('source') in ('compact', 'clear') and os.path.exists(mark):
            os.remove(mark)
    elif mode == 'pre':
        if re.search(r'\bgit\s+(commit|push|merge)\b', cmd) and not os.path.exists(mark):
            print(json.dumps({'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'deny',
                'permissionDecisionReason':
                    '本会话第一次提交、推送或合并：先单独跑一条 `bash scripts/read-rules.sh git`，'
                    '整份读完后再执行（读规则和动作不要写在同一行）。'}}, ensure_ascii=False))
    elif mode == 'post':
        out = json.dumps(d.get('tool_response', ''), ensure_ascii=False)   # 结构不细究，按内容判
        if 'read-rules.sh git' in cmd and '# topic: git' in out and '# end-of-topic: git' in out:
            open(mark, 'w').close()

try:
    main()
except Exception as e:                      # 判定器自己出错：放行并告警，不卡死
    print(f'read-gate 出错，已放行：{e}', file=sys.stderr)
```

这段代码在本地用模拟的 hook 输入实测过七种情形：未读就推送被拒、读规则的命令本身放行、只读一半不记已读、读完后放行、压缩后重新拦下、读规则和推送写在同一行被拒、输入坏了放行不卡死。几点说明：

- 拒绝用的是 `PreToolUse` 的 JSON 输出（`permissionDecision: "deny"`），理由会转给 agent 看。
- `tool_response` 的具体结构官方文档没有细说，所以按**内容**判断（找头尾标），不依赖字段名。
- 标记按 `session_id` 分开存，`.claude/read-gate/` 要加进 `.gitignore`。
- 只管了 git 一类动作。部署、写生产库照同样的写法各加一个 topic。

#### 几条实现细节，都是踩出来的

- **读规则的命令本身绝不能被拦**，否则死锁。判定要匹配具体的动作（`git push`），不能匹配 `git` 这个词。
- **读规则和动作要分成两条命令。** 写在同一行里的话，规则要等整条命令返回才进上下文，动作已经执行了，所以这种写法一律拦。
- **门槛判定器出错时放行并告警。** 它是协作层，不是硬护栏；判定器有 bug 就把 agent 一次提交都卡死，代价更大。真正的硬门槛在 git 钩子和部署脚本里。
- **规则文件要小于工具的输出上限。** 作者项目里实测：超限时 hook 看到的输出同样只有预览，尾标对不上，「整份读完」就永远判不成立，门槛变成了单纯拦人。不同版本的行为可能不同，所以用自测把每份必读规则的体量钉在上限以下。

### 大文件按章读

工具对单次命令输出有上限（Claude Code 里由 `bashOutputMaxChars` 控制），超出部分会被存盘，上下文里只留开头一小段预览，外加一句很不显眼的提示。对 agent 来说，这很容易变成「以为读了，其实没读到」。

做法是给读规则的脚本加两种读法：

```bash
bash scripts/read-rules.sh design-spec --toc               # 目录：每节标题、行号、字节数
bash scripts/read-rules.sh design-spec --section 配色       # 只取标题里含「配色」的那一节
```

- 超过上限的大文件只许按章读，整份读直接拒绝。
- **超限提示打在输出的第一行。** 被截断后只有开头那一小段能留下，提示放在末尾等于没提示。
- 切分章节要识别代码围栏：围栏里以 `##` 开头的行是内容，不是标题。
- 节选不能带「整份读完」的头尾标，否则动作门槛会把节选误记成读过全文。

## 代价与适用条件

- 四条通道要靠脚本和 hook 维护。起步时只需要「入口文件 + 几份按路径规则」，等某类动作真的出过事，再给它加门槛。
- 按路径送达、hook、技能都是 Claude Code 的机制。换别的工具，通道的落点要重新找；工具没有对应机制的，只能退回入口文件里的指路表，加上 git 钩子兜底。
- 通道越多，越要防「同一条规则在两条通道里各写一份」，见第 3 章。

## 踩过的坑

### 按路径规则在「读到文件时」送达，而不是「你打算做那件事时」

部署规则曾经按路径生效，路径是部署脚本本身。结果，一个**没有先读部署脚本、直接执行它**的会话，上下文里一条部署规则都没有。护栏恰好在最需要它的那条路径上失效。

**修法**：撤不回的动作不能只靠按路径送达，改用动作门槛（先读后做）。

### 新建文件时，规则在写完之后才到

按路径规则在文件被读入或写入时才送达。新建一个文件时，第一次写入就没看着规则写：规则是在写完的返回结果里才注入的。

**修法**：在入口文件里列出哪些目录有按路径规则，规定在这些目录下新建文件前，先读同目录任意一个已有文件，让规则提前到位。

### 输出被截断却没有任何报错

一份要求「动手前先读」的规则悄悄长到约 134KB，远超输出上限：每次读它，上下文里都只留下开头那段预览，而这件事一直没人发现。

**修法**：按章读，超限提示打在第一行，并用自测守住每份必读规则的体量。

### 规则文件里的 `@` 导入会在开场就被展开

在按路径规则里用 `@path` 引用另一份文件，本意是「碰到这类文件时再读」。实测这个引用会在**会话开场**就被展开、整份载入，完全不受 `paths:` 约束，等于每个会话都多背了一整份规则。

**修法**：规则文件里不写 `@` 导入，改写成纯文本路径，让 agent 需要时自己去读；用自测扫描所有规则文件里的 `@`。

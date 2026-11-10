# Chapter 3 · How Rules Reach the Agent

## The problem

The rules are written, and the agent still makes the very mistakes the rules describe. Looking back, most of the time it isn't disobedience: **at that moment the rule simply wasn't in its context**:

- Every rule gets stuffed into `CLAUDE.md`, which keeps growing; the chance that any one rule is followed keeps dropping, until you're forced to cut;
- The rules live in a separate file, but the agent doesn't know it should read it, or knows and doesn't;
- It does read it, but the file is too big, so the tool puts only the first small chunk into context and silently cuts the rest;
- The session gets compacted, and the rules read at session start are lost along with it.

## The idea

**A rule doesn't count just because it's written in the repo. You have to design "when, and through which channel" it enters the agent's context.**

Different rules need different delivery timing. Sorted by "when is it needed," there are four channels:

| Channel | When it enters context | What goes there | Where it lives in Claude Code |
|---|---|---|---|
| **Always-on at session start** | At the start of every session; reloaded automatically after compaction | What every session needs: project overview, red lines, language and time conventions, sensitive-data rules | `CLAUDE.md` + files under `.claude/rules/` without `paths:` |
| **Path-scoped delivery** | When reading or writing files that match certain paths | What's only needed when touching a certain kind of file: backend conventions, the design spec index, doc library rules | Files under `.claude/rules/` with `paths:` |
| **Read-before-act gate** | Before the first time a certain kind of action is performed | The full procedure for irreversible actions: commit and push, deploy, change production data | A `PreToolUse` hook blocks it and requires reading the whole file first |
| **On-demand invocation** | When the agent decides it's needed, or the user names it | Multi-step procedures: writing a spec, review, checking production data, doing UI | `.claude/skills/` |

This chapter goes into how the text layer is delivered; for the full picture of all the layers, see Chapter 1. There is also a fifth category that doesn't rely on delivery at all: **things that must hold go into no channel; they go into machine gates** (Chapter 2).

### Trade-offs of each channel

- **Always-on at session start should be small and firm.** It takes up context in every session. Put in only facts, red lines, and pointers to "where to find it," not procedural detail. Give it a total size cap, and enforce the cap with a script.
- **Path-scoped delivery is the cheapest, but its trigger condition is easy to get wrong** (see "Pitfalls we hit" below).
- **The action gate is the most reliable, but it adds friction.** Use it only for the few actions where "getting it wrong can't be undone."
- **On-demand skills are the most flexible, and also the most dependent on the agent's own initiative.** Make each skill's description state clearly "when to use it and when not to," and add a trigger table in the entry file: "what you're about to do → which skill to run first."

## In practice

### The entry file is only a map

`CLAUDE.md` holds no rule text. It holds just three things: which delivery paths the rules have, what to read before each kind of action (the trigger table), and how to read large files. For example, the trigger table below.

> Note: the `scripts/read-rules.sh` (rule-reading script) in this book's examples, and the slash commands `/spec`, `/design-ui` and `/db-readonly`, are all scripts and skills **you need to build in your own project**. They are not built into Claude Code, and this repo doesn't provide them either. What `read-rules.sh` does is simple: given a name (topic), it prints the full text of the matching rule file, with a marker line at each end, `# topic: <name>` and `# end-of-topic: <name>`; it also supports `--toc` to list the contents and `--section` to fetch a single section (see "Read large files section by section" below).

```markdown
## Before you start: action trigger points

| What you're about to do | Run first |
|---|---|
| Commit / merge / push / create a branch | `bash scripts/read-rules.sh git` (gated: committing without reading it gets blocked) |
| Deploy / ssh into a server | `bash scripts/read-rules.sh deploy` (same as above) |
| Before changing the behavior of code, rules or scripts | `/spec` steps 1–3: read-only investigation → the four-line report → recommended tier |
| Change the UI | `/design-ui` |
| Query production data to draw a conclusion | `/db-readonly` (read-only) |
| Before answering questions about architecture or current state | Read the doc map `docs/README.md` first (Chapter 8) |
```

### Path-scoped rules: one rule file, one set of paths

```markdown
---
paths:
  - "server/**"
  - "shared/**"
---

# Backend conventions

- Time columns always use a timezone-aware type; ...
```

In our experience, a path-scoped rule file works best when it covers only one kind of file, and its body holds only the few points that are "easiest to get wrong when touching this kind of file, and can't be seen from reading the code." The full explanation goes in the living docs; the rule only points to it.

### Read before you act: the action gate

This is a layer between written rules and hard gates (Chapter 2): it guarantees that before the agent acts, the corresponding rules are in its context. It doesn't guarantee the agent follows them, and it isn't proof of authorization. It's implemented with Claude Code hooks:

1. `PreToolUse`: work out which kind of action the command about to run belongs to (commit, push, deploy, write to the production database...). If this session hasn't yet read the corresponding rules, refuse to run it and say which rule-reading command to run first.
2. `PostToolUse`: confirm that the rule-reading command **read the whole file**. The test is that both the header marker and the footer marker are in the output; partial reads like `| head` don't count. Once confirmed, record "read in this session."
3. `SessionStart`: when the session is compacted or cleared, the rules that were read are no longer in context, so the record is invalidated and they must be read again.

#### Minimal implementation

Wire three hooks into `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse":  [{ "matcher": "Bash", "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/scripts/hooks/read-gate.py\" pre" }] }],
    "PostToolUse": [{ "matcher": "Bash", "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/scripts/hooks/read-gate.py\" post" }] }],
    "SessionStart": [{ "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/scripts/hooks/read-gate.py\" start" }] }]
  }
}
```

`scripts/hooks/read-gate.py`:

```python
#!/usr/bin/env python3
"""Read before you act: before the first commit / push / merge in a session, the git rules must be read in full."""
import json, os, re, sys

def main():
    mode = sys.argv[1]                      # pre | post | start
    d = json.load(sys.stdin)
    sid = re.sub(r'[^A-Za-z0-9_-]', '', d.get('session_id', ''))[:64]
    if not sid:
        return                              # no session id: let it through; a broken gate must not lock the human out
    state = os.path.join(os.environ.get('CLAUDE_PROJECT_DIR', '.'), '.claude', 'read-gate')
    os.makedirs(state, exist_ok=True)
    mark = os.path.join(state, sid + '.git')
    cmd = (d.get('tool_input') or {}).get('command', '')

    if mode == 'start':                     # after compaction or clear, the rules read earlier are gone: invalidate the mark
        if d.get('source') in ('compact', 'clear') and os.path.exists(mark):
            os.remove(mark)
    elif mode == 'pre':
        if re.search(r'\bgit\s+(commit|push|merge)\b', cmd) and not os.path.exists(mark):
            print(json.dumps({'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'deny',
                'permissionDecisionReason':
                    'First commit, push or merge in this session: run `bash scripts/read-rules.sh git` on its own first, '
                    'read it in full, then run this (don\'t put the rule read and the action on the same line).'}}, ensure_ascii=False))
    elif mode == 'post':
        out = json.dumps(d.get('tool_response', ''), ensure_ascii=False)   # don't rely on the structure; judge by content
        if 'read-rules.sh git' in cmd and '# topic: git' in out and '# end-of-topic: git' in out:
            open(mark, 'w').close()

try:
    main()
except Exception as e:                      # the checker itself failed: let it through and warn, don't block
    print(f'read-gate error, let through: {e}', file=sys.stderr)
```

This code was tested locally with simulated hook input against seven cases: pushing without reading is refused; the rule-reading command itself is let through; reading only half doesn't record a read; after a full read, the action is let through; after compaction it's blocked again; putting the rule read and the push on the same line is refused; bad input is let through instead of blocking. A few notes:

- Refusal uses `PreToolUse`'s JSON output (`permissionDecision: "deny"`), and the reason is passed on to the agent.
- The official docs don't spell out the exact structure of `tool_response`, so the check goes by **content** (looking for the header and footer markers), not by field names.
- Marks are stored separately per `session_id`; add `.claude/read-gate/` to `.gitignore`.
- Only git actions are covered here. For deploys and writes to the production database, add a topic for each in the same way.

#### A few implementation details, all learned the hard way

- **The rule-reading command itself must never be blocked**, or you get a deadlock. The check must match the specific action (`git push`), not the word `git`.
- **Keep the rule read and the action as two separate commands.** If they're on the same line, the rules only enter context once the whole command returns, by which point the action has already run. So that form is always blocked.
- **When the gate's checker fails, let it through and warn.** It's a collaboration layer, not a hard guardrail; a buggy checker that blocks every single commit the agent tries costs more. The real hard gates live in git hooks and deploy scripts.
- **Rule files must be smaller than the tool's output cap.** Measured in the author's project: when a file is over the cap, the hook also sees only the preview, the footer marker never matches, "read in full" can never be satisfied, and the gate turns into a plain blocker. Behavior may differ across versions, so use a self-test to pin every must-read rule file below the cap.

### Read large files section by section

The tool caps the output of a single command (in Claude Code this is controlled by `bashOutputMaxChars`). Anything over the cap is saved to disk; the context keeps only a small preview of the beginning, plus a very easy-to-miss notice. For the agent, this easily turns into "thought it read the file, but never actually saw it."

The fix is to give the rule-reading script two extra ways to read:

```bash
bash scripts/read-rules.sh design-spec --toc               # contents: each section's heading, line number, byte count
bash scripts/read-rules.sh design-spec --section Colors    # fetch only the section whose heading contains "Colors"
```

- Large files over the cap may only be read section by section; a whole-file read is refused outright.
- **Put the over-the-cap notice on the first line of the output.** After truncation only the small chunk at the beginning survives; a notice at the end is no notice at all.
- Section splitting must recognize code fences: inside a fence, a line starting with `##` is content, not a heading.
- An excerpt must not carry the "read in full" header and footer markers, or the action gate will mistake the excerpt for a full read.

## Costs and when it applies

- The four channels have to be maintained with scripts and hooks. For the minimal starting set, see the README's "How to read" section; add a gate to a kind of action only after that action has actually caused trouble.
- Path-scoped delivery, hooks and skills are all Claude Code mechanisms. With a different tool, you'll have to find where each channel lands again; where the tool has no equivalent mechanism, the only fallback is the pointer table in the entry file, backed up by git hooks.
- The more channels you have, the more you need to guard against "the same rule written once in each of two channels"; see Chapter 4.

## Pitfalls we hit

### Path-scoped rules are delivered "when the file is read," not "when you intend to do the thing"

The deploy rules were once path-scoped, with the path being the deploy script itself. As a result, a session that **ran the deploy script directly without reading it first** had not a single deploy rule in its context. The guardrail failed on exactly the path where it was needed most.

**Fix**: irreversible actions can't rely on path-scoped delivery alone; use the action gate (read-before-act gate) instead.

### When creating a new file, the rules arrive after it's written

Path-scoped rules are delivered only when a file is read or written. When a new file is created, the first write happens without the rules in view: the rules are injected only in the result returned after the write.

**Fix**: list in the entry file which directories have path-scoped rules, and require that before creating a new file in one of those directories, the agent first reads any existing file in the same directory, so the rules arrive ahead of time.

### Output was truncated with no error at all

A rule that required "read before you start" quietly grew to about 134KB, far over the output cap: every time it was read, only the preview at the beginning stayed in context, and nobody noticed for a long time.

**Fix**: read section by section, put the over-the-cap notice on the first line, and use a self-test to enforce the size of every must-read rule file.

### `@` imports in rule files are expanded at session start

Using `@path` in a path-scoped rule to reference another file was meant as "read it only when touching this kind of file." In testing, the reference was expanded and loaded in full **at session start**, completely ignoring `paths:`, which meant every session carried an entire extra rule file.

**Fix**: don't write `@` imports in rule files; write a plain-text path instead and let the agent read it when needed; use a self-test to scan every rule file for `@`.

# Chapter 2 · Written Rules Are Not Enforcement

## The problem

When you first start coding with AI, the most natural move is to write the rules into `CLAUDE.md` or a rule file: "run the tests before deploying", "don't modify a migration that's already committed", "no direct pushes to the main branch". The more you write, the safer you feel.

Then one day, something the rules spelled out clearly happens anyway.

## The idea

**A rule file isn't configuration. It's the same kind of thing as a prompt: text stuffed into the context, relying on the model to comply on its own.**

Most of the time the model complies, but "most of the time" isn't enough. In the situations below, written rules fail silently:

- A new session, a subagent, or a compacted context, and the rule never gets delivered;
- The rule is delivered, but the task at hand pulls the model's attention away;
- Rules conflict with each other, and the model picks one.

So rules have to be split into two kinds:

| | Written rules | Machine gates |
|---|---|---|
| What it is | Instructions in the context | A check that blocks if it doesn't pass |
| Good for | Judgment, trade-offs, style preferences | Irreversible actions, things that go wrong silently |
| Examples | "Investigate the impact before making a change" | git hooks, lint, tests, pre-deploy check scripts |

The criterion is a single sentence: **if this goes wrong, can it be undone afterward? If it can't be undone, or nobody would notice it went wrong, it can't rely on text alone.**

## In practice

### Enforcement mechanisms, ranked by strength

1. **git's pre-commit hook**: whichever tool the agent is using, it fires on any `git commit` on this machine, regardless of whether CI ran or has quota left. In a personal project it's usually the strongest line. But know its two gaps: `core.hooksPath` is local config and has to be set once for every clone; and `git commit --no-verify` bypasses it outright (to stop the agent from doing that, match this flag in `PreToolUse`).
2. **Pre-deploy check script**: put it in the first step of the deploy script; if a check fails, `exit 1`, never touching the server.
3. **Lint and tests**: including assertions that scan the source code, such as "this layer must not import that layer".
4. **CI**: the last line. It can catch what local hooks miss (edits made directly on the web, fresh clones, `--no-verify`), but in personal projects it often doesn't run because of quota or trigger conditions.

### Minimal example: main-branch protection

```bash
#!/bin/bash
# .githooks/pre-push — block force-pushes to and deletion of main
while read -r local_ref local_sha remote_ref remote_sha; do
  if [ "$remote_ref" = "refs/heads/main" ]; then
    if [ "$local_sha" = "0000000000000000000000000000000000000000" ]; then
      echo "Deleting the remote main is not allowed" >&2; exit 1
    fi
    if [ "$remote_sha" != "0000000000000000000000000000000000000000" ] \
       && ! git merge-base --is-ancestor "$remote_sha" "$local_sha"; then
      echo "Force-pushing main is not allowed" >&2; exit 1
    fi
  fi
done
```

Enable it:

```bash
chmod +x .githooks/pre-push && git config core.hooksPath .githooks
```

When the hook file lacks execute permission, git ignores it (printing a one-line hint at most) and the push succeeds as usual: exactly the kind of failure described in "A guardrail existing ≠ a guardrail working" below. So after installing it, deliberately force-push once to confirm it really gets blocked.

### Between written rules and hard gates: read before you act

Some rules are too long and too dependent on judgment to write as checks, yet too important to count on the model remembering them, such as the deploy procedure or the git branching model. You can add a middle layer: the first time the agent is about to commit, push or deploy, block it and require it to read the corresponding rules in full before letting it through.

What this gate buys is **visibility and friction**, not proof of authorization: it guarantees the rules are in the model's context before it acts, not that it follows them. The real hard gates are still the ones above. For the implementation and a minimal example, see "Read before you act: the action gate" in Chapter 3.

## Costs and when it applies

- Machine gates need maintenance: criteria go stale, and false blocks train a "red doesn't matter" habit. Put gates only on things that are irreversible or go wrong silently.
- Decide in advance what happens when a gate itself breaks. A helper gate like the read-before-act gate lets things through when it errors (Chapter 3); a hard gate like the deploy check should fail closed.
- Hooks aren't unforgeable either: an agent that can change its own config can also change its own hooks. They guard against carelessness, not malice.

## Pitfalls we hit

### A gate written only in the rules has zero coverage

The deploy rules listed the three most important gates: tests must all pass, the human must explicitly confirm before deploying, and the working tree must be clean. Day to day, everything was fine. Only when a new tool that couldn't read these rules was brought in did it come to light: the deploy script had **not a single line implementing** any of the three gates. Nothing had gone wrong before only because the sessions in use all happened to be able to read the rules; the hole itself had been there all along.

**Fix**: write the three gates into the first step of the deploy script. The rule file says only "which script the gates are in" and no longer lists the criteria one by one (a copied list will miss items).

### A guardrail existing ≠ a guardrail working

A formatting-check hook was treated as the only enforcement backstop, and it failed four separate times: the match condition never matched, the inline script got eaten by the shell, a hardcoded field name couldn't retrieve the path, and the hand-written criteria had never been compared against the authoritative implementation. **Not one of these produced any signal.** "Didn't run" and "judged correctly" have the same symptom: silence.

**Lesson**:

- Guardrails need a self-test (a set of positive and negative cases that ships with the guardrail script; one run tells you whether it can still correctly block and let through): construct a real input and run it, pin it into the self-test, and hook the self-test into pre-commit.
- Write the negative case first: while the check function doesn't exist yet, the self-test should go red. Confirm it really can go red, then write the implementation.
- A checker that's a hand-written reimplementation should be diffed against the authoritative implementation on a regular schedule. "It runs" doesn't mean "it judges correctly".
- When a new check goes red across the board as soon as it's live, verify the checker itself first, before blaming the existing code.

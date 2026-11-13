---
name: delegate-task
description: Write a complete brief and pick model and effort before spawning a subagent. Use whenever you are about to delegate work to a subagent or a parallel agent.
---

# Delegate a task

1. **Scope.** Write the one assignment you are delegating now. If it is really two independent jobs, make two briefs.
2. **Classify** it with the table in AGENTS.md: mechanical, bounded or judgement. Pick tier and effort.
3. **Pick the agent.** Claude Code: `scout` (read-only exploration), `runner` (mechanical commands), `reviewer`
   (review), or a general-purpose agent for implementation. Codex: see `references/codex-agents.md`.
4. **Fill the brief** below. Paste facts you already have. A brief under 5 lines is almost always missing context.
5. **Spawn** with the model and effort set explicitly, even when they match the default.
6. **Check** the result against the definition of done before you use it.

## Brief template

```
Goal: <one sentence> because <why>.
Context: <paths, symbols, findings so far, decisions already made>.
Do: <steps or the ticket text>.
Do not: <files, APIs, behaviours that are off limits>.
Done when: <command that passes, or question answered>.
Return: <format and maximum length>.
Model/effort: <tier>/<effort> — <class> because <one reason>.
```

## Parallel work
- Spawn independent briefs in one message so they run at the same time.
- Writers in parallel need separate files, or separate worktrees.
- Collect all results, then integrate yourself. Do not ask one subagent to merge another's work.

# AGENTS.md: subagent delegation and model routing

The lead session plans, decides and talks to the human. Subagents do bounded work. Pick the cheapest model
and effort that can do each assignment well, and say so explicitly every time you spawn one.

## Classify each assignment before spawning
Classify the work you are delegating now, not the parent ticket. Choose the tier directly; do not trial-run tiers.

| Class | Examples | Tier | Effort |
|---|---|---|---|
| Mechanical | run tests and report, grep for a known symbol, rename from an exact list, format, capture screenshots | small (Claude: `haiku`; Codex: the fast/mini model) | low |
| Bounded | implement one ticket with clear acceptance criteria, write tests for one module, summarise 5–20 files | mid (Claude: `sonnet`; Codex: default model) | medium–high |
| Judgement | architecture, debugging across modules, conflicting evidence, security or data-loss risk, final review | top (Claude: `opus`; Codex: strongest model on the plan) | high–xhigh |

- If getting it slightly wrong is cheap to catch, use the lower tier.
- Never downgrade the human's chosen lead model. Routing applies to subagents only.
- Reassess when a subagent's work changes materially. Do not restart a working subagent only to change its tier.

## Write a full brief
Subagents start without your conversation. They know only what you put in the brief. Every brief contains:
1. Goal in one sentence, and why it matters.
2. Exact paths, symbols, commands and constraints. Paste the facts you already found; do not make it rediscover them.
3. What it must not touch.
4. Definition of done: the command that must pass or the question that must be answered.
5. Output format: what to return and how long (for example "a list of file:line findings, max 15 lines").
Use the `delegate-task` skill to write the brief.

## When to delegate, when not to
- Delegate broad reading (more than ~5 files) so raw file contents stay out of the lead context.
- Delegate independent tasks in parallel, in one message. Never run two writers on the same files at once.
- Do small, sequential work yourself: a one- or two-file change at a known location costs more to brief than to do.
- Tripwire: if a change will touch three or more files, or needs a browser, stop and delegate.

## After a subagent returns
- Read its report; spot-check one claim against the code before relying on it.
- Reviewers never edit what they review. If a review finds problems, a writer fixes them.

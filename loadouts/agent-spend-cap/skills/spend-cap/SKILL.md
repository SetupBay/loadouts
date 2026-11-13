---
name: spend-cap
description: Put one daily and monthly spend cap across headless Claude Code, Codex and Antigravity CLI runs, with a per-run budget and a ledger, and set the provider-side limits that are the real hard stop. Use when scripting agent runs, running agents in loops or CI, or when someone asks what the agents cost.
---

# One spend cap across agents

Each agent has its own meter. Claude Code reports dollars (`total_cost_usd` in `--output-format json`) and can stop
itself (`--max-budget-usd`). Codex (`codex exec --json`) and Antigravity (`agy -p --output-format json`) report
tokens only, and neither has a budget flag. A loop that mixes them can spend all three budgets before anyone looks.
`scripts/spend_guard.py` puts one ledger and one cap in front of all of them.

## Set up

```bash
mkdir -p .agent-spend
cp <this skill>/references/caps.example.json .agent-spend/caps.json
echo ".agent-spend/" >> .gitignore
```

Edit `caps.json` with the user: `daily_usd`, `monthly_usd`, `per_run_usd` and `max_runs_per_day`. Add `prices` for
Codex and Antigravity in USD per million tokens, taken from the provider's current price page for the model in use.
Never guess a price. With zero prices those agents count towards `max_runs_per_day` only.

## Run every headless agent through it

```bash
python3 spend_guard.py run --agent claude --task fix-tests -- claude -p "Fix the failing tests" --output-format json
python3 spend_guard.py run --agent codex  --task triage    -- codex exec --json "Triage open issues"
python3 spend_guard.py run --agent agy    --task docs      -- agy -p "Update the README" --output-format json
python3 spend_guard.py report
```

- Before the run it refuses with exit 3 if today's or this month's cap is reached, if what is left is under
  `min_run_usd`, or if `max_runs_per_day` is used up. Treat exit 3 as "stop the loop", not "retry".
- For Claude Code it appends `--max-budget-usd` set to the smaller of `per_run_usd` and what is left today, so the
  agent stops itself.
- Codex and Antigravity cannot be stopped mid-run. Their cost is estimated from tokens afterwards, and a run can
  overshoot by up to one run. Keep `per_run_usd` small and the prompts scoped.
- Exit 4 means no cost or usage was found in the output (wrong flags, or a crash). Look before running again.
- The ledger is `.agent-spend/ledger.jsonl`: one line per run with agent, task, exit code, cost and token usage.
  Days and months use the machine's time zone.

## Provider-side limits are the hard stop

The guard only sees runs that go through it. Set the provider's own limit as well, and read
`references/provider-limits.md` for where each one lives. Antigravity's `useG1Credits` setting must stay `false`
unless the user decides to pay for credits after the plan quota runs out.

## Rules

- Never raise a cap, add credits, change a plan or turn on overage billing yourself. Report the refusal and the
  ledger totals, and let the user decide.
- Never route around the guard by calling an agent directly in a loop.
- Interactive sessions are outside the ledger. Say so when you report spend.
- Costs here are estimates. The provider's bill is the truth.

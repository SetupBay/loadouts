# AGENTS.md: shared spend cap for coding agents

This repository runs coding agents headless (scripts, loops, CI): Claude Code, Codex and Antigravity CLI. Every
headless run goes through one spend guard with a shared daily and monthly cap. The user sets the caps; agents never
change them.

## Rules
- Run headless agents only through the `spend-cap` skill's guard:
  `python3 spend_guard.py run --agent <claude|codex|agy> --task <name> -- <agent command>`.
- Use the machine-readable output each agent documents (`--output-format json` for Claude Code and Antigravity,
  `--json` for Codex) so the guard can read cost or tokens.
- Exit 3 from the guard means a cap is reached. Stop, report the totals from `spend_guard.py report`, and wait for
  the user. Do not retry, and do not call the agent directly instead.
- Never raise caps, buy credits, change plans, turn on overage or usage credits, or set Antigravity's
  `useG1Credits` to `true`.
- Keep each run small: one task, scoped files, a clear stop condition. Prefer one agent per task to fan-outs.
- Report spend as an estimate, and say that interactive sessions are not in the ledger.

## Done means
- The ledger has a line for every headless run, and `spend_guard.py report` is under the caps.

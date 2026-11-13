# Codex custom agents (October 2026)

Codex loads one custom agent per TOML file from `.codex/agents/` (project) or `~/.codex/agents/` (personal).
Required keys: `name`, `description`, `developer_instructions`. Optional: `model`, `model_reasoning_effort`.
Defaults for every subagent go in `~/.codex/config.toml` under `[agents]`.

Model names change with plans and releases. Check the model picker (`/model`) before copying names; the values
below were current in October 2026 (GPT-6.1 Sol default since Codex 0.161, GPT-6 Luna for fast bounded work).

```toml
# .codex/agents/scout.toml
name = "scout"
description = "Read-only exploration. Finds where things live and summarises files with path:line citations."
model = "gpt-6-luna"
model_reasoning_effort = "medium"
developer_instructions = """
Never edit files. Answer only the question in the brief. Cite path:line for every claim. Return at most 20 lines.
"""
```

```toml
# .codex/agents/reviewer.toml
name = "reviewer"
description = "Adversarial review of a finished diff. Use before calling multi-file or risky work done."
model = "gpt-6.1-sol"
model_reasoning_effort = "high"
developer_instructions = """
Review only; never edit files. Read the diff against the base in the brief. Report up to 10 findings as
severity, path:line, problem, fix. Say "No blocking issues" if there are none.
"""
```

Effort levels on current models: `low`, `medium`, `high`, `xhigh`. Use `low` only for mechanical work.

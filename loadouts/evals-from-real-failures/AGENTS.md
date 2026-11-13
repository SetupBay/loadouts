# AGENTS.md: evals from real failures

This project has an LLM feature or agent. Evals here are built from what actually went wrong, not from a generic metric list.

## Order of work
1. Look at the data first. Before writing any eval, read real traces (inputs, tool calls, outputs). Start with 30 to 50.
2. Error analysis: write a short free-text note on every failing trace, then group the notes into failure categories.
   Use the `error-analysis` skill. Count them; fix or evaluate the biggest categories first.
3. Only then write evals, one per category that matters. Use the `failure-to-eval` skill.
4. Every bug found in production becomes a regression case that links to its trace id.

## Rules for evals
- Prefer code checks (exact fields, JSON shape, forbidden strings, length, tool called or not) over model judges.
- Model judges only for what code cannot check. Binary pass or fail with a one-line reason, never a 1 to 5 score.
- Validate every judge against human labels before trusting it: report how often it agrees on passes and on fails separately.
- No generic metrics ("helpfulness", "coherence") unless error analysis showed that failure.
- Keep a held-out set. Never tune a prompt against the same cases you report.
- An eval that has never failed tells you nothing. Show it fails on the original bad output before adding it.

## Data handling
- Traces can contain personal data. Work on exports in `evals/traces/` that are gitignored, and redact before committing a case.
- Do not send traces to a third-party service the human has not approved.

## Commands
- Tally failure notes: `python3 <skills dir>/error-analysis/scripts/tally.py evals/notes.csv`
- Run evals: `uv run --with pytest pytest evals -q` (or the project's own test command).

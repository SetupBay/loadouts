---
name: failure-to-eval
description: Turn a failure category or a production bug into regression eval cases with code checks, and a model judge only when needed. Use after error analysis, or when a bad output is reported.
---

# Failure to eval

Inputs: a failure category from error analysis (or a reported bug) with real trace ids.

1. For each trace, add one case to `evals/cases/<category>.jsonl`:
   `{"id": "...", "source": "<trace id>", "input": {...}, "expect": {...}}`. Redact personal data first.
   `source` is required: every case points at the real trace it came from.
2. Write the expectation as code checks wherever possible. `references/test_regressions.py` supports:
   `contains`, `not_contains`, `max_chars`, `json_keys` (output must be JSON with these keys) and `matches` (regex).
3. Copy `references/test_regressions.py` to `evals/` and set `EVAL_TARGET=module:function` to the function that produces
   the output (it receives the case `input` dict and returns a string).
4. Prove the case bites: run it against the original bad output (or the old prompt) and confirm it fails. Then confirm it
   passes on the fix. A case that never failed is not a regression test.
5. Only if code cannot express the check, write a judge prompt from `references/judge-prompt.md`: one failure mode per
   judge, binary pass or fail, a one-line reason. Label 20 or more outputs by hand, run the judge on them and report its
   agreement on passes and on fails separately. Do not use the judge until both are acceptable to the human.
6. Run `uv run --with pytest pytest evals -q` and add the command to CI next to the unit tests.

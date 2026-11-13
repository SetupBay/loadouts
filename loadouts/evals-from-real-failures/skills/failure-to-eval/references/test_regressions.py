"""Regression evals built from real failures. Each case in evals/cases/*.jsonl links to the trace it came from.

Set EVAL_TARGET=module:function. The function takes the case's input dict and returns the output string.
"""

import importlib
import json
import os
import re
from pathlib import Path

import pytest

CASES_DIR = Path(os.environ.get("EVAL_CASES", Path(__file__).parent / "cases"))


def load_cases():
    cases = []
    for path in sorted(CASES_DIR.glob("*.jsonl")):
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                case = json.loads(line)
                case["_where"] = f"{path.name}:{n}"
                cases.append(case)
    return cases


def target():
    module, _, func = os.environ["EVAL_TARGET"].partition(":")
    return getattr(importlib.import_module(module), func)


def check(output: str, expect: dict) -> list[str]:
    problems = []
    for s in expect.get("contains", []):
        if s not in output:
            problems.append(f"missing {s!r}")
    for s in expect.get("not_contains", []):
        if s in output:
            problems.append(f"contains forbidden {s!r}")
    if "max_chars" in expect and len(output) > expect["max_chars"]:
        problems.append(f"{len(output)} chars > {expect['max_chars']}")
    if "matches" in expect and not re.search(expect["matches"], output):
        problems.append(f"does not match /{expect['matches']}/")
    if "json_keys" in expect:
        try:
            data = json.loads(output)
            absent = [k for k in expect["json_keys"] if k not in data]
            if absent:
                problems.append(f"JSON missing keys {absent}")
        except (json.JSONDecodeError, TypeError):
            problems.append("output is not JSON")
    return problems


CASES = load_cases()


def test_every_case_links_to_a_real_trace():
    assert CASES, f"no cases in {CASES_DIR}"
    unlinked = [c["_where"] for c in CASES if not str(c.get("source", "")).strip()]
    assert not unlinked, f"cases without a source trace id: {unlinked}"


@pytest.mark.parametrize("case", CASES, ids=[c.get("id", c["_where"]) for c in CASES])
def test_case(case):
    output = target()(case["input"])
    problems = check(output, case["expect"])
    assert not problems, f"{case['_where']} (trace {case.get('source')}): {'; '.join(problems)}"

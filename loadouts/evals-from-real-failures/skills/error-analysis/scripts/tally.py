#!/usr/bin/env python3
"""Tally failure categories from an error-analysis notes CSV (trace_id,pass,note,category)."""

import argparse
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("notes", type=Path)
    ap.add_argument("--examples", type=int, default=3, help="example trace ids per category")
    args = ap.parse_args()

    with args.notes.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    missing = {"trace_id", "pass", "note", "category"} - set(rows[0].keys() if rows else [])
    if missing:
        print(f"error: missing columns: {', '.join(sorted(missing))}", file=sys.stderr)
        return 2

    failing = [r for r in rows if r["pass"].strip() == "0"]
    counts = Counter(r["category"].strip() for r in failing if r["category"].strip())
    examples = defaultdict(list)
    for r in failing:
        cat = r["category"].strip()
        if cat and len(examples[cat]) < args.examples:
            examples[cat].append(r["trace_id"])
    uncategorised = [r["trace_id"] for r in failing if not r["category"].strip()]

    print(f"traces: {len(rows)}, failing: {len(failing)} ({len(failing) / max(len(rows), 1):.0%})")
    print("| category | count | share of failures | examples |")
    print("| --- | --- | --- | --- |")
    for cat, n in counts.most_common():
        print(f"| {cat} | {n} | {n / len(failing):.0%} | {', '.join(examples[cat])} |")
    if uncategorised:
        print(f"uncategorised failures: {', '.join(uncategorised)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Shared spend cap for headless agent runs (Claude Code, Codex, Antigravity CLI).

    spend_guard.py run --agent claude --task fix-tests -- claude -p "..." --output-format json
    spend_guard.py run --agent codex  --task triage    -- codex exec --json "..."
    spend_guard.py run --agent agy    --task docs      -- agy -p "..." --output-format json
    spend_guard.py report

Before a run it refuses (exit 3) when today's or this month's spend has reached the cap, or
when what is left is less than one run's budget. For Claude Code it adds --max-budget-usd so
the agent itself stops at the smaller of the per-run cap and what is left. Codex and
Antigravity report tokens, not money, so their cost comes from the prices you set in
caps.json, and they cannot be stopped mid-run: the provider-side limit is the hard stop.

Config: .agent-spend/caps.json (or SPEND_DIR). Ledger: .agent-spend/ledger.jsonl.
Standard library only. Costs are estimates; the provider's bill is the truth.
"""

import argparse
import datetime as dt
import fcntl
import json
import os
import subprocess
import sys
from pathlib import Path

SPEND_DIR = Path(os.environ.get("SPEND_DIR", ".agent-spend"))
CAPS = SPEND_DIR / "caps.json"
LEDGER = SPEND_DIR / "ledger.jsonl"
REFUSED = 3


def load_caps():
    if not CAPS.exists():
        sys.exit(f"spend_guard: {CAPS} not found; copy the spend-cap skill's caps.example.json there")
    caps = json.loads(CAPS.read_text())
    for key in ("daily_usd", "monthly_usd", "per_run_usd"):
        if not isinstance(caps.get(key), (int, float)) or caps[key] <= 0:
            sys.exit(f"spend_guard: caps.json needs a positive {key}")
    return caps


def now():
    return dt.datetime.now().astimezone()


def totals(at):
    """Spend today, spend this month and runs today, in the local time zone."""
    day = month = 0.0
    runs = 0
    if LEDGER.exists():
        for line in LEDGER.read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            ts = dt.datetime.fromisoformat(rec["ts"]).astimezone(at.tzinfo)
            cost = rec.get("cost_usd") or 0.0
            if (ts.year, ts.month) == (at.year, at.month):
                month += cost
                if ts.date() == at.date():
                    day += cost
                    runs += 1
    return round(day, 4), round(month, 4), runs


def price(caps, agent, usage):
    p = (caps.get("prices") or {}).get(agent)
    if not p:
        return None
    mtok = 1_000_000
    cached = usage.get("cached_input_tokens", usage.get("cache_read_tokens", 0))
    fresh_input = max(usage.get("input_tokens", 0) - cached, 0)
    output = usage.get("output_tokens", 0) + usage.get("reasoning_output_tokens", usage.get("thinking_tokens", 0))
    cost = (
        fresh_input * p["input_per_mtok"]
        + cached * p.get("cached_input_per_mtok", p["input_per_mtok"])
        + output * p["output_per_mtok"]
    ) / mtok
    return round(cost, 6)


def parse(agent, stdout):
    """Return (cost_usd or None, usage dict) from the agent's documented JSON output."""
    usage, cost = {}, None
    lines = [ln for ln in stdout.splitlines() if ln.strip().startswith("{")]
    if agent == "claude":
        for ln in reversed(lines):
            obj = json.loads(ln)
            if "total_cost_usd" in obj:
                return float(obj["total_cost_usd"]), obj.get("usage", {})
    elif agent == "codex":
        for ln in lines:
            obj = json.loads(ln)
            if obj.get("type") == "turn.completed":
                for k, v in obj.get("usage", {}).items():
                    usage[k] = usage.get(k, 0) + v
    elif agent == "agy":
        for ln in reversed(lines):
            obj = json.loads(ln)
            result = obj.get("result", obj) if obj.get("event") in (None, "result") else None
            if result and "usage" in result:
                usage = result["usage"]
                break
    return cost, usage


def required_output_flags(agent, cmd):
    if agent == "claude" and "--output-format" not in cmd:
        return "add --output-format json (or stream-json) so the cost can be read"
    if agent == "codex" and "--json" not in cmd:
        return "add --json so token usage can be read"
    if agent == "agy" and "--output-format" not in cmd:
        return "add --output-format json (or stream-json) so token usage can be read"
    return None


def run(args):
    caps = load_caps()
    cmd = args.cmd[1:] if args.cmd and args.cmd[0] == "--" else args.cmd
    if not cmd:
        sys.exit("spend_guard: give the agent command after --")
    problem = required_output_flags(args.agent, cmd)
    if problem:
        sys.exit(f"spend_guard: {problem}")
    if args.agent in ("codex", "agy") and not (caps.get("prices") or {}).get(args.agent):
        sys.exit(f"spend_guard: no prices for {args.agent} in caps.json, so its spend cannot be capped")

    SPEND_DIR.mkdir(parents=True, exist_ok=True)
    lock = open(SPEND_DIR / ".lock", "w")
    fcntl.flock(lock, fcntl.LOCK_EX)
    at = now()
    day, month, runs = totals(at)
    left = min(caps["daily_usd"] - day, caps["monthly_usd"] - month)
    budget = round(min(caps["per_run_usd"], left), 2)
    max_runs = caps.get("max_runs_per_day")
    if max_runs is not None and runs >= max_runs:
        print(f"spend_guard: REFUSED {args.agent}/{args.task}: {runs} runs today, cap {max_runs}", file=sys.stderr)
        return REFUSED
    if left <= 0 or budget < caps.get("min_run_usd", 0.05):
        print(
            f"spend_guard: REFUSED {args.agent}/{args.task}: today ${day:.2f} of ${caps['daily_usd']:.2f}, "
            f"month ${month:.2f} of ${caps['monthly_usd']:.2f}",
            file=sys.stderr,
        )
        return REFUSED
    if args.agent == "claude" and "--max-budget-usd" not in cmd:
        cmd = cmd + ["--max-budget-usd", f"{budget:.2f}"]
    print(f"spend_guard: {args.agent}/{args.task} budget ${budget:.2f} (left today ${left:.2f})", file=sys.stderr)
    fcntl.flock(lock, fcntl.LOCK_UN)

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    sys.stdout.write(proc.stdout)
    cost, usage = parse(args.agent, proc.stdout)
    if cost is None:
        cost = price(caps, args.agent, usage)
    rec = {
        "ts": now().isoformat(timespec="seconds"),
        "agent": args.agent,
        "task": args.task,
        "exit": proc.returncode,
        "cost_usd": cost,
        "estimated_from_tokens": args.agent != "claude",
        "usage": usage,
    }
    if cost is None:
        rec["note"] = "no cost or usage found in the output; recorded as unknown"
    fcntl.flock(lock, fcntl.LOCK_EX)
    with LEDGER.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    fcntl.flock(lock, fcntl.LOCK_UN)
    shown = "unknown" if cost is None else f"${cost:.4f}"
    print(f"spend_guard: recorded {args.agent}/{args.task} {shown}", file=sys.stderr)
    if cost is None:
        return 4
    if cost > budget:
        print(f"spend_guard: WARNING run cost {shown} exceeded its ${budget:.2f} budget", file=sys.stderr)
    return proc.returncode


def report(_args):
    caps = load_caps()
    at = now()
    day, month, runs = totals(at)
    by_agent = {}
    if LEDGER.exists():
        for line in LEDGER.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                ts = dt.datetime.fromisoformat(rec["ts"]).astimezone(at.tzinfo)
                if (ts.year, ts.month) == (at.year, at.month):
                    a = by_agent.setdefault(rec["agent"], [0, 0.0])
                    a[0] += 1
                    a[1] += rec.get("cost_usd") or 0.0
    print(f"today  ${day:.2f} of ${caps['daily_usd']:.2f} ({runs} run(s))")
    print(f"month  ${month:.2f} of ${caps['monthly_usd']:.2f}")
    for agent, (runs, cost) in sorted(by_agent.items()):
        print(f"{agent:<7}{runs} run(s) ${cost:.2f} this month")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="command", required=True)
    r = sub.add_parser("run")
    r.add_argument("--agent", required=True, choices=["claude", "codex", "agy"])
    r.add_argument("--task", required=True)
    r.add_argument("cmd", nargs=argparse.REMAINDER)
    r.set_defaults(func=run)
    sub.add_parser("report").set_defaults(func=report)
    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()

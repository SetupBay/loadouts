#!/usr/bin/env python3
"""Run a queue of agent tasks unattended: one git worktree and branch per task, a per-task and total
dollar budget, Claude Code's unattended retry settings, a finish-line check, and a morning report.

Usage:
  python3 night_shift.py run [--plan night-shift.json]   run every task in the plan, in order
  python3 night_shift.py report                           rewrite .night-shift/report.md from the ledger

Plan (night-shift.json):
  {
    "budget_usd_total": 6.00,
    "agent": ["claude", "-p", "--output-format", "json", "--max-turns", "40", "--permission-mode", "acceptEdits"],
    "tasks": [ {"id": "fix-flaky-date-test", "goal": "...", "check": "pytest -q tests/test_dates.py", "budget_usd": 2.00} ]
  }
The script appends --max-budget-usd (the smaller of the task budget and what is left) and the prompt.
Results go to .night-shift/ledger.jsonl and .night-shift/report.md. Branches are named night/<date>-<id>.
It never pushes, merges or deletes a branch. Exit 0 when every task ran, 3 when the budget stopped the queue.
Standard library only.
"""
import datetime
import json
import os
import subprocess
import sys

STATE = ".night-shift"
WATCHDOG_DEFAULTS = {
    "CLAUDE_CODE_RETRY_WATCHDOG": "1",                            # keep retrying 429/529 instead of failing at 3 a.m.
    "CLAUDE_CODE_RETRY_WATCHDOG_MAX_WAIT_MS": "1800000",          # but give up on one request after 30 minutes of waits
    "CLAUDE_CODE_RETRY_WATCHDOG_MAX_USAGE_LIMIT_WAIT_MS": "3600000",  # and end it if the usage limit resets more than 1 h away
}
MIN_TASK_USD = 0.50


def sh(cmd, cwd=None, timeout=None, env=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)


def die(msg, code=1):
    print(f"night-shift: {msg}", file=sys.stderr)
    sys.exit(code)


def load_plan(path):
    try:
        plan = json.load(open(path))
    except (OSError, ValueError) as e:
        die(f"cannot read {path}: {e}")
    agent = plan.get("agent") or []
    if not agent:
        die("plan has no agent command")
    bypass = any(a.startswith("--dangerously") for a in agent) or "bypassPermissions" in agent
    if bypass and os.environ.get("NIGHT_SHIFT_SANDBOXED") != "1":
        die("refusing to run with permission checks bypassed outside a sandbox (set NIGHT_SHIFT_SANDBOXED=1 only inside a container or VM)")
    if "--max-budget-usd" in agent:
        die("leave --max-budget-usd out of the agent command; the script sets it per task from the budget")
    ids = [t.get("id", "") for t in plan.get("tasks", [])]
    if not ids or any(not i or not i.replace("-", "").isalnum() for i in ids) or len(set(ids)) != len(ids):
        die("every task needs a unique id made of letters, digits and hyphens")
    for t in plan["tasks"]:
        if not t.get("goal") or not t.get("check"):
            die(f"task {t['id']} needs a goal and a check command (the finish line)")
    return plan


def spent_tonight(ledger, night):
    return sum(r.get("cost_usd", 0) for r in ledger if r.get("night") == night)


def read_ledger():
    p = os.path.join(STATE, "ledger.jsonl")
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def prompt_for(task, branch):
    return (
        f"{task['goal']}\n\n"
        f"Finish line: `{task['check']}` exits 0 in this worktree. Run it yourself before you stop.\n"
        f"You are on branch {branch} in your own worktree. Commit your work to this branch with a clear message.\n"
        "Do not push, open pull requests, merge, or change files outside this worktree. Do not edit or skip tests to reach the finish line.\n"
        "If you cannot reach the finish line, commit what you have, then end with a short note: what is blocking, what you tried."
    )


def run(plan_path):
    plan = load_plan(plan_path)
    if sh(["git", "rev-parse", "--is-inside-work-tree"]).returncode != 0:
        die("run this from the root of a git repository")
    os.makedirs(os.path.join(STATE, "worktrees"), exist_ok=True)
    exclude = sh(["git", "rev-parse", "--git-path", "info/exclude"]).stdout.strip()
    if exclude and f"/{STATE}/" not in (open(exclude).read() if os.path.exists(exclude) else ""):
        os.makedirs(os.path.dirname(exclude), exist_ok=True)
        with open(exclude, "a") as fh:
            fh.write(f"\n/{STATE}/\n")  # keep worktrees and the ledger out of git status
    night = datetime.date.today().isoformat()
    total = float(plan.get("budget_usd_total", 0))
    ledger_path = os.path.join(STATE, "ledger.jsonl")
    stopped = False
    env = dict(os.environ)
    for k, v in WATCHDOG_DEFAULTS.items():
        env.setdefault(k, v)
    for task in plan["tasks"]:
        left = round(total - spent_tonight(read_ledger(), night), 4)
        budget = round(min(float(task.get("budget_usd", left)), left), 2)
        if budget < MIN_TASK_USD:
            print(f"STOP before {task['id']}: ${left:.2f} left of ${total:.2f} tonight")
            stopped = True
            break
        branch = f"night/{night}-{task['id']}"
        wt = os.path.join(STATE, "worktrees", task["id"])
        if os.path.exists(wt):
            die(f"{wt} already exists; review and remove it (git worktree remove) before re-running {task['id']}")
        r = sh(["git", "worktree", "add", "-q", "-b", branch, wt])
        if r.returncode != 0:
            die(f"git worktree add failed for {task['id']}: {r.stderr.strip()}")
        cmd = [*plan["agent"], "--max-budget-usd", f"{budget:.2f}", prompt_for(task, branch)]
        print(f"run {task['id']}: budget ${budget:.2f} (left ${left:.2f}), branch {branch}")
        started = datetime.datetime.now()
        try:
            a = sh(cmd, cwd=wt, timeout=int(task.get("timeout_min", 90)) * 60, env=env)
            out, code = a.stdout, a.returncode
        except subprocess.TimeoutExpired:
            out, code = "", "timeout"
        try:
            res = json.loads(out.strip().splitlines()[-1]) if out.strip() else {}
        except ValueError:
            res = {}
        cost = float(res.get("total_cost_usd") or 0)
        chk = sh(["bash", "-c", task["check"]], cwd=wt, timeout=1800)
        ahead = sh(["git", "rev-list", "--count", f"HEAD..{branch}"]).stdout.strip() or "0"
        row = {
            "night": night, "task": task["id"], "branch": branch, "agent_exit": code,
            "subtype": res.get("subtype", "no-json"), "turns": res.get("num_turns"), "cost_usd": round(cost, 4),
            "check": task["check"], "check_ok": chk.returncode == 0, "commits": int(ahead),
            "minutes": round((datetime.datetime.now() - started).total_seconds() / 60, 1),
            "note": (res.get("result") or "").strip().splitlines()[-1][:200] if res.get("result") else "",
        }
        with open(ledger_path, "a") as fh:
            fh.write(json.dumps(row) + "\n")
        print(f"  {task['id']}: {'PASS' if row['check_ok'] else 'FAIL'} check, {row['subtype']}, ${cost:.4f}, {row['commits']} commit(s)")
    write_report()
    return 3 if stopped else 0


def write_report():
    ledger = read_ledger()
    if not ledger:
        die("no runs in the ledger yet")
    night = ledger[-1]["night"]
    rows = [r for r in ledger if r["night"] == night]
    lines = [f"# Night shift {night}", "", "| Task | Finish line | Result | Cost | Turns | Commits | Branch |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        result = "passed" if r["check_ok"] else "not reached"
        if r["subtype"] not in ("success",):
            result += f" ({r['subtype']})"
        lines.append(f"| {r['task']} | `{r['check']}` | {result} | ${r['cost_usd']:.2f} | {r['turns'] if r['turns'] is not None else '-'} | {r['commits']} | `{r['branch']}` |")
    spent = sum(r["cost_usd"] for r in rows)
    passed = sum(1 for r in rows if r["check_ok"])
    lines += ["", f"Spent ${spent:.2f} on {len(rows)} task(s); {passed} reached the finish line.", ""]
    for r in rows:
        if r["note"]:
            lines.append(f"- {r['task']}: {r['note']}")
    lines += ["", "Review each branch (`git log -p main..<branch>`) before merging. Nothing was pushed.",
              "Remove a worktree when done with it: `git worktree remove .night-shift/worktrees/<task>`."]
    with open(os.path.join(STATE, "report.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines[:4 + len(rows) + 2]))


def main(argv):
    if not argv or argv[0] not in ("run", "report"):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    if argv[0] == "report":
        write_report()
        return 0
    plan = argv[argv.index("--plan") + 1] if "--plan" in argv else "night-shift.json"
    return run(plan)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

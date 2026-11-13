#!/usr/bin/env python3
"""Check that every package manager a project uses has a release-age cooldown, and that nobody turned it off.

Standard library only (Python 3.11+ for tomllib).  python3 cooldown_check.py [project dir] [--min-days 1]

Package managers are detected from lockfiles: package-lock.json (npm), pnpm-lock.yaml (pnpm), bun.lock or bun.lockb
(Bun), uv.lock (uv). Settings read: .npmrc min-release-age (days), pnpm-workspace.yaml minimumReleaseAge (minutes),
bunfig.toml [install] minimumReleaseAge (seconds), pyproject.toml [tool.uv] or uv.toml exclude-newer (durations
such as "7 days" or ISO 8601 "P7D").
"""
import re
import sys
import tomllib
from pathlib import Path

args = sys.argv[1:]
root = Path(next((a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or args[i - 1] != "--min-days")), ".")).resolve()
min_days = float(args[args.index("--min-days") + 1]) if "--min-days" in args else 1.0
out, used = [], []


def add(level, tool, msg):
    out.append((level, tool, msg))


def judge(tool, days, where):
    if days is None:
        return
    if days <= 0:
        add("fix", tool, f"cooldown turned off in {where}")
    elif days < min_days:
        add("warn", tool, f"cooldown is {days:g} day(s) in {where}; the project wants at least {min_days:g}")
    else:
        add("ok", tool, f"{days:g} day(s) ({where})")


def uv_days(value):
    if value is False or value is None:
        return None
    v = str(value).strip().lower()
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(hours?|days?|weeks?)", v)
    if m:
        n, unit = float(m.group(1)), m.group(2)
        return n / 24 if unit.startswith("hour") else n * 7 if unit.startswith("week") else n
    m = re.fullmatch(r"p(?:(\d+)w)?(?:(\d+)d)?(?:t(?:(\d+)h)?)?", v)
    if m and any(m.groups()):
        w, d, h = (int(x or 0) for x in m.groups())
        return w * 7 + d + h / 24
    return "date"  # an absolute timestamp: a frozen snapshot, not a rolling cooldown


if (root / "package-lock.json").exists():
    used.append("npm")
    npmrc = (root / ".npmrc").read_text() if (root / ".npmrc").exists() else ""
    m = re.search(r"^\s*min-release-age\s*=\s*(\d+(?:\.\d+)?)\s*$", npmrc, re.M)
    if m:
        judge("npm", float(m.group(1)), ".npmrc min-release-age")
    else:
        add("fix", "npm", "no min-release-age in .npmrc (npm 11.10+ supports it; value in days)")

if (root / "pnpm-lock.yaml").exists():
    used.append("pnpm")
    ws = (root / "pnpm-workspace.yaml").read_text() if (root / "pnpm-workspace.yaml").exists() else ""
    m = re.search(r"^minimumReleaseAge:\s*(\d+)\s*$", ws, re.M)
    if m:
        judge("pnpm", int(m.group(1)) / 1440, "pnpm-workspace.yaml minimumReleaseAge")
    else:
        add("warn", "pnpm", "minimumReleaseAge not set: relies on pnpm's default (1440 minutes in current pnpm); set it explicitly")

if (root / "bun.lock").exists() or (root / "bun.lockb").exists():
    used.append("bun")
    cfg = tomllib.loads((root / "bunfig.toml").read_text()) if (root / "bunfig.toml").exists() else {}
    secs = (cfg.get("install") or {}).get("minimumReleaseAge")
    if secs is None:
        add("fix", "bun", "no [install] minimumReleaseAge in bunfig.toml (value in seconds)")
    else:
        judge("bun", float(secs) / 86400, "bunfig.toml minimumReleaseAge")

if (root / "uv.lock").exists():
    used.append("uv")
    val, where = None, None
    if (root / "uv.toml").exists():
        val, where = tomllib.loads((root / "uv.toml").read_text()).get("exclude-newer"), "uv.toml"
    if val is None and (root / "pyproject.toml").exists():
        val = ((tomllib.loads((root / "pyproject.toml").read_text()).get("tool") or {}).get("uv") or {}).get("exclude-newer")
        where = "pyproject.toml [tool.uv]"
    days = uv_days(val)
    if days is None:
        add("fix", "uv", 'no exclude-newer (use a rolling duration such as "7 days")')
    elif days == "date":
        add("warn", "uv", f"exclude-newer in {where} is a fixed date, not a rolling cooldown; it freezes updates")
    else:
        judge("uv", days, f"{where} exclude-newer")

if not used:
    add("warn", "-", "no npm, pnpm, Bun or uv lockfile found")
for level, tool, msg in out:
    print(f"{level:<4} {tool}: {msg}")
fixes = sum(1 for o in out if o[0] == "fix")
warns = sum(1 for o in out if o[0] == "warn")
print(f"package managers: {', '.join(used) or 'none'}; {fixes} to fix, {warns} warnings")
sys.exit(1 if fixes else 0)

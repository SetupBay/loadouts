#!/usr/bin/env python3
"""Audit SKILL.md descriptions against the limits agents apply to their skill listings.

Usage: python3 skill_listing.py [--context TOKENS] DIR [DIR ...]
  DIR is a skills folder (.claude/skills, .agents/skills, a plugin's skills/) or one skill folder.
  --context  the model's context window in tokens, for the listing-budget estimate (default 200000).

Checks each skill's front matter, then the whole listing:
  error  no description; description + when_to_use over Claude Code's 1,536-character cap (cut short);
         front matter that is not valid simple YAML (an unquoted ": " inside a value, a missing closing ---).
  warn   name differs from the folder; no "use when" style trigger; first sentence over 200 characters;
         two skills whose descriptions share most of their words (the agent can't tell them apart).
  info   listing size against Claude Code's budget (1% of the context window) and Codex's
         (2% of the context window, 8,000 characters when the window is unknown). Characters/4 is an estimate.
Exit 1 if any error, else 0. Standard library only; read-only.
"""
import os
import re
import sys

CLAUDE_ENTRY_CAP = 1536
TRIGGER = re.compile(r"\b(use (it |this )?(when|for|after|before|if|whenever)|when the user|triggers? (on|when|include)|invoke when)\b", re.I)
STOP = set("a an and are as at be by for from if in into is it its of on or the this to use used when with your you that".split())


def parse_front_matter(text):
    """Return (dict, error). Supports key: value, quoted values, and | or > block scalars."""
    if not text.startswith("---"):
        return None, "no front matter (the file must start with ---)"
    lines = text.splitlines()
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None, "front matter has no closing ---"
    data, i = {}, 1
    while i < end:
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):(?:\s+(.*))?$", line)
        if not m:
            if line.startswith((" ", "\t")):
                i += 1
                continue
            return None, f"line {i + 1}: not a 'key: value' line"
        key, val = m.group(1), (m.group(2) or "").strip()
        if val in ("|", ">", "|-", ">-", "|+", ">+"):
            block = []
            i += 1
            while i < end and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            data[key] = ("\n" if val.startswith("|") else " ").join(b for b in block if b).strip()
            continue
        if val[:1] in "\"'":
            q = val[0]
            if not val.endswith(q) or len(val) < 2:
                return None, f"line {i + 1}: {key} opens a {q} quote that never closes on that line"
            val = val[1:-1]
        elif ": " in val:
            return None, f"line {i + 1}: {key} contains ': ' without quotes, so YAML reads it as a nested key; quote the value"
        elif val == "":
            # nested mapping (metadata:, hooks:) - skip its indented lines
            i += 1
            while i < end and lines[i].startswith((" ", "\t")):
                i += 1
            data[key] = {}
            continue
        data[key] = val
        i += 1
    return data, None


def skill_dirs(paths):
    for p in paths:
        if os.path.isfile(os.path.join(p, "SKILL.md")):
            yield p
            continue
        if not os.path.isdir(p):
            print(f"skip {p}: not a folder", file=sys.stderr)
            continue
        for name in sorted(os.listdir(p)):
            d = os.path.join(p, name)
            if os.path.isfile(os.path.join(d, "SKILL.md")):
                yield d


def words(s):
    return {w for w in re.findall(r"[a-z0-9][a-z0-9.+#-]*", s.lower()) if w not in STOP and len(w) > 2}


def main(argv):
    context = 200000
    if "--context" in argv:
        i = argv.index("--context")
        context = int(argv[i + 1])
        del argv[i:i + 2]
    if not argv or any(a.startswith("-") for a in argv):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    errors = warns = 0
    listing, seen = [], []
    for d in skill_dirs(argv):
        folder = os.path.basename(os.path.normpath(d))
        text = open(os.path.join(d, "SKILL.md"), encoding="utf-8").read()
        fm, err = parse_front_matter(text)
        tag = f"{folder}:"
        if err:
            print(f"error {tag} {err}")
            errors += 1
            continue
        name = fm.get("name") or folder
        if any(n == name for n, _ in seen):
            print(f"same  {tag} also installed in another folder (one per agent); counted once")
            continue
        desc = fm.get("description") if isinstance(fm.get("description"), str) else ""
        when = fm.get("when_to_use") if isinstance(fm.get("when_to_use"), str) else ""
        hidden = str(fm.get("disable-model-invocation", "")).lower() == "true"
        if not desc:
            print(f"error {tag} no description (Codex requires one; Claude Code falls back to the first line of the body)")
            errors += 1
            continue
        combined = (desc + (" " + when if when else "")).strip()
        before = errors
        if len(combined) > CLAUDE_ENTRY_CAP:
            print(f"error {tag} description + when_to_use is {len(combined)} characters; Claude Code cuts each entry at {CLAUDE_ENTRY_CAP}, so the end is lost")
            errors += 1
        if fm.get("name") and fm["name"] != folder:
            print(f"warn  {tag} name '{fm['name']}' differs from the folder '{folder}'; some agents list one, some the other")
            warns += 1
        if not hidden and not TRIGGER.search(combined):
            print(f"warn  {tag} no trigger clause; add 'Use when ...' with the words a user would actually type")
            warns += 1
        first = re.split(r"(?<=[.!?])\s", desc, maxsplit=1)[0]
        if len(first) > 200:
            print(f"warn  {tag} first sentence is {len(first)} characters; put the key use case first, in under 200")
            warns += 1
        w = words(combined)
        for other, ow in seen:
            if w and ow and len(w & ow) / len(w | ow) >= 0.6:
                print(f"warn  {tag} description overlaps '{other}' ({len(w & ow)} shared words); say what makes each one different")
                warns += 1
        seen.append((name, w))
        if not hidden:
            listing.append((name, len(name) + len(combined[:CLAUDE_ENTRY_CAP]) + 4))
        print(f"{'ok   ' if errors == before else 'fix  '} {tag} {len(combined)} chars{' (hidden from the model: disable-model-invocation)' if hidden else ''}")
    total = sum(n for _, n in listing)
    claude_budget = int(context * 0.01 * 4)
    codex_budget = int(context * 0.02 * 4)
    print(f"listing: {len(listing)} skill(s), about {total} characters (~{total // 4} tokens)")
    print(f"budget: Claude Code 1% of {context} tokens ~ {claude_budget} chars: {'fits' if total <= claude_budget else 'OVER, least-used descriptions get dropped'}")
    print(f"budget: Codex 2% of {context} tokens ~ {codex_budget} chars (8000 if the window is unknown): {'fits' if total <= codex_budget else 'OVER, descriptions get shortened'}")
    print(f"skill-listing: {errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

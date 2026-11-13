#!/usr/bin/env python3
"""Flag prose patterns that read as machine-written.

Usage: python3 prose_lint.py [--allow word,word] [--max-dashes N] FILE [FILE ...]
Skips fenced code blocks, inline code, block quotes and YAML front matter.
Prints "path:line rule "match" -> suggestion" and exits 1 if anything is found. Standard library only.
"""
import re
import sys

W = r"\b"
VOCAB = [
    (r"delv(?:e|es|ed|ing)|deep[- ]dive", "look at, read, check"),
    (r"leverag(?:e|es|ed|ing)", "use"),
    (r"utili[sz](?:e|es|ed|ing|ation)", "use"),
    (r"boasts", "has"),
    (r"seamless(?:ly)?", "say what happens, or cut"),
    (r"robust(?:ly|ness)?", "say what it withstands"),
    (r"tapestry|testament", "cut"),
    (r"pivotal|crucial", "important, and say why"),
    (r"underscor(?:e|es|ed|ing)", "show"),
    (r"showcas(?:e|es|ed|ing)", "show"),
    (r"foster(?:s|ed|ing)?", "build, encourage"),
    (r"empower(?:s|ed|ing)?|unlock(?:s|ed|ing)? (?:the |your |their )?(?:full )?potential|elevat(?:e|es|ed|ing) your", "say what it lets someone do"),
    (r"cutting[- ]edge|game[- ]chang(?:er|ing)|revolutionary|next[- ]level|best[- ]in[- ]class|industry[- ]leading", "cut"),
    (r"vibrant|intricate|meticulous(?:ly)?|multifaceted", "cut, or be specific"),
    (r"navigat(?:e|ing) the (?:complexities|challenges|world)", "handle, deal with"),
    (r"ever[- ](?:evolving|changing) (?:landscape|world)|in the (?:\w+ )?landscape of", "cut"),
    (r"(?:a|the|this|your) journey", "cut (figurative 'journey')"),
]
PHRASES = [
    ("not-just", r"\b(?:it'?s|this is|is) not just (?:a |an |about )?[^.,;]{1,40}[,;:]\s*(?:it'?s|but)\b", "say what it is"),
    ("not-only", r"\bnot only\b[^.]{1,80}\bbut also\b", "say what it is"),
    ("whether-youre", r"\bwhether you'?re (?:a |an )?\w+ or\b", "cut"),
    ("fast-paced", r"\bin today'?s (?:fast[- ]paced|digital|modern) (?:world|age|landscape)\b", "cut"),
    ("serves-as", r"\b(?:stands|serves) as (?:a|an|the)\b", "is"),
    ("plays-a-role", r"\bplays? an? (?:crucial|key|pivotal|vital|important) role\b", "say what it does"),
    ("chat-opener", r"^(?:certainly|absolutely|great question|of course)[!,.]", "cut"),
    ("chat-closer", r"\b(?:i hope this helps|let me know if you (?:have|need)|happy to help)\b", "cut"),
    ("lets-dive", r"\blet'?s (?:dive|jump|get started)\b", "cut"),
    ("recap", r"^(?:in conclusion|in summary|overall),", "cut the recap"),
    ("additionally", r"^additionally,", "also, or a new paragraph"),
    ("unverified-proof", r"\b\d{1,3}(?:,\d{3})+\+|\btrusted by (?:thousands|millions|teams|developers)\b", "give a source and date, or cut"),
]
EMOJI_BULLET = re.compile(r"^\s*(?:[-*]\s+)?[\U0001F300-\U0001FAFF\u2600-\u27BF\u2705\u274C]\s*\S|^#+\s*[\U0001F300-\U0001FAFF\u2600-\u27BF]")
DASH = "\u2014"


def strip_inline(line):
    return re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), line)


def lint(path, allow, max_dashes):
    out = []
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    in_code = False
    in_front = bool(lines) and lines[0].strip() == "---"
    para_dashes = 0
    vocab = [(re.compile(W + "(?:" + p + ")" + W, re.I), s) for p, s in VOCAB]
    phrases = [(n, re.compile(p, re.I), s) for n, p, s in PHRASES]
    for n, raw in enumerate(lines, 1):
        if in_front:
            if n > 1 and raw.strip() == "---":
                in_front = False
            continue
        if raw.lstrip().startswith(("```", "~~~")):
            in_code = not in_code
            continue
        if in_code or raw.lstrip().startswith(">"):
            continue
        if not raw.strip():
            para_dashes = 0
            continue
        line = strip_inline(raw)
        text = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", line)
        text = re.sub(r"^#+\s*", "", text).strip()
        for rx, sugg in vocab:
            for m in rx.finditer(line):
                if m.group(0).lower() not in allow:
                    out.append((n, "ai-vocabulary", m.group(0), sugg))
        for name, rx, sugg in phrases:
            m = rx.search(text)
            if m and m.group(0).lower() not in allow:
                out.append((n, name, m.group(0), sugg))
        if EMOJI_BULLET.search(line):
            out.append((n, "emoji-bullet", line.strip()[:20], "plain bullet or heading"))
        if len(re.findall(r"\*\*[^*]+\*\*", line)) >= 3:
            out.append((n, "bold-spam", "**", "bold one thing at most"))
        para_dashes += line.count(DASH)
        if line.count(DASH) and para_dashes > max_dashes:
            out.append((n, "em-dash", DASH, "colon, comma or a new sentence"))
    return [(path, *f) for f in out]


def main(argv):
    allow, max_dashes, files = set(), 1, []
    it = iter(argv[1:])
    for a in it:
        if a == "--allow":
            allow |= {w.strip().lower() for w in next(it, "").split(",") if w.strip()}
        elif a == "--max-dashes":
            max_dashes = int(next(it, "1"))
        else:
            files.append(a)
    if not files:
        print(__doc__.strip())
        return 2
    findings = []
    for f in files:
        findings += lint(f, allow, max_dashes)
    for path, n, rule, match, sugg in findings:
        print(f'{path}:{n} {rule} "{match}" -> {sugg}')
    print(f"{len(findings)} finding{'s' if len(findings) != 1 else ''} in {len(files)} file{'s' if len(files) != 1 else ''}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

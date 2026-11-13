#!/usr/bin/env python3
"""List SwiftUI previews for RenderPreview and flag views and previews that will waste a render.

Standard library only, runs anywhere (no Xcode needed).
  python3 preview_check.py <project dir> [--targets]

--targets prints one line per preview: <project-relative path> <previewDefinitionIndexInFile> <name>,
which is what Xcode MCP's RenderPreview takes.

fix:  a #Preview that touches the network or shared singletons (URLSession.shared, .shared, UserDefaults.standard),
      a preview that reads secrets from the environment
warn: a public or top-level View struct with no preview in its file, a file with more than 6 previews
"""
import re
import sys
from pathlib import Path

PREVIEW = re.compile(r'^\s*#Preview\b(?:\s*\(\s*"([^"]*)")?|^\s*struct\s+(\w+)\s*:\s*PreviewProvider\b', re.M)
VIEW = re.compile(r'^(?:public\s+|internal\s+)?struct\s+(\w+)\s*(?:<[^>]*>)?\s*:\s*(?:[\w.]+\s*,\s*)*View\b', re.M)
LIVE = [
    (re.compile(r'URLSession\.shared'), "uses URLSession.shared: previews should use fixture data, not the network"),
    (re.compile(r'\b\w+\.shared\b(?!\s*=)'), "uses a .shared singleton: inject a preview instance instead"),
    (re.compile(r'UserDefaults\.standard'), "uses UserDefaults.standard: previews then depend on the Mac's state"),
    (re.compile(r'ProcessInfo\.processInfo\.environment'), "reads the environment: keep secrets out of previews"),
]


def preview_blocks(src):
    """Yield (index, name, body) for each preview, body = text up to the next preview or end of file."""
    marks = list(PREVIEW.finditer(src))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(src)
        name = m.group(1) or m.group(2) or f"preview {i}"
        yield i, name, src[m.start():end]


def main(argv):
    if not argv or argv[0].startswith("-"):
        print(__doc__.strip().splitlines()[2].strip())
        return 2
    root = Path(argv[0]).resolve()
    show_targets = "--targets" in argv
    out, targets, files = [], [], 0
    for f in sorted(root.rglob("*.swift")):
        if any(p in f.parts for p in (".build", "DerivedData", "Pods", "Tests")) or f.name.endswith("Tests.swift"):
            continue
        files += 1
        rel = f.relative_to(root).as_posix()
        src = f.read_text(encoding="utf-8", errors="replace")
        blocks = list(preview_blocks(src))
        for i, name, body in blocks:
            targets.append((rel, i, name))
            seen = set()
            for rx, msg in LIVE:
                if rx.search(body) and msg not in seen:
                    if "singleton" in msg and "URLSession.shared" in body:
                        continue
                    seen.add(msg)
                    out.append(("fix", rel, f'preview {i} ("{name}") {msg}'))
        if len(blocks) > 6:
            out.append(("warn", rel, f"{len(blocks)} previews in one file; each RenderPreview call builds again"))
        if not blocks:
            for m in VIEW.finditer(src):
                out.append(("warn", rel, f"{m.group(1)} has no #Preview, so RenderPreview can't show it"))
    for level, rel, msg in out:
        print(f"{level:<4} {rel}: {msg}")
    if show_targets:
        for rel, i, name in targets:
            print(f"target {rel} {i} {name}")
    fixes = sum(1 for o in out if o[0] == "fix")
    print(f"swift files: {files}; previews: {len(targets)}; {fixes} to fix, {len(out) - fixes} warnings")
    return 1 if fixes else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

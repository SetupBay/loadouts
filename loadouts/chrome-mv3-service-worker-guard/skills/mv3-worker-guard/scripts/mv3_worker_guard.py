#!/usr/bin/env python3
"""Find Manifest V2 extension APIs, and code that breaks in an MV3 service worker, in a Chrome extension's source.

Usage: python3 mv3_worker_guard.py [PATH ...]        (default: the current folder)
       python3 mv3_worker_guard.py --list            (print every rule)

A "guard: ok" comment on a line silences its warnings (never its errors).
Prints one line per finding:  path:line: level [rule] what is wrong -> what to use
Exit 0 when nothing at "error" level is found, 1 when something is, 2 on bad usage.
Standard library only. Read-only: it never edits a file and makes no network calls.
"""
import fnmatch
import os
import re
import sys

# (rule id, level, regex, message, file patterns). Patterns run against each line with comments removed.
RULES = [
    ('browser-action', 'error', '\\bchrome\\.(browserAction|pageAction)\\b',
     'chrome.browserAction/pageAction were removed in MV3 -> chrome.action', ['*.js', '*.mjs', '*.ts', '*.tsx', '*.jsx']),
    ('tabs-execute-script', 'error', '\\bchrome\\.tabs\\.(executeScript|insertCSS|removeCSS)\\(',
     'tabs.executeScript/insertCSS/removeCSS were removed in MV3 -> chrome.scripting.executeScript/insertCSS/removeCSS (permission scripting)', ['*.js', '*.mjs', '*.ts', '*.tsx', '*.jsx']),
    ('extension-legacy', 'error', '\\bchrome\\.extension\\.(getBackgroundPage|getViews|getURL|sendRequest|onRequest|connect|sendMessage|onMessage|getExtensionTabs)\\b',
     'chrome.extension.* messaging and page access are gone in MV3 -> chrome.runtime.sendMessage/onMessage/getURL; there is no background page', ['*.js', '*.mjs', '*.ts', '*.tsx', '*.jsx']),
    ('runtime-background-page', 'error', '\\bchrome\\.runtime\\.getBackgroundPage\\(',
     'MV3 has no background page -> message the service worker with chrome.runtime.sendMessage', ['*.js', '*.mjs', '*.ts', '*.tsx', '*.jsx']),
    ('tabs-legacy', 'error', '\\bchrome\\.tabs\\.(getSelected|getAllInWindow|sendRequest|onActiveChanged|onSelectionChanged)\\b',
     'removed tabs API -> chrome.tabs.query({ active: true, currentWindow: true }) / tabs.sendMessage / tabs.onActivated', ['*.js', '*.mjs', '*.ts', '*.tsx', '*.jsx']),
    ('webrequest-blocking', 'error', '[\\"\']blocking[\\"\']',
     'blocking webRequest is not available to MV3 extensions (except force-installed) -> chrome.declarativeNetRequest rules', ['*.js', '*.mjs', '*.ts', '*.tsx', '*.jsx']),
    ('remote-code', 'error', '\\beval\\(|\\bnew Function\\(|setTimeout\\(\\s*[\\"\'`]',
     'MV3 forbids running strings as code -> ship the code in the package', ['*.js', '*.mjs', '*.ts', '*.tsx', '*.jsx']),
    ('remote-script-tag', 'error', '\\.src\\s*=\\s*[\\"\'`]https?://|import\\(\\s*[\\"\'`]https?://',
     'MV3 forbids remotely hosted code -> bundle the script', ['*.js', '*.mjs', '*.ts', '*.tsx', '*.jsx']),
    ('sw-dom', 'error', '\\b(document|window)\\.|\\blocalStorage\\b|\\bsessionStorage\\b|\\bXMLHttpRequest\\b|\\balert\\(',
     'service workers have no DOM, window, localStorage or XMLHttpRequest -> chrome.storage, fetch, and an offscreen document for DOM work', ['sw.js', 'sw.ts', 'service-worker.js', 'service-worker.ts', 'service_worker.js', 'service_worker.ts', 'background.js', 'background.ts', '*-worker.js', '*-worker.ts', '*_worker.js', '*_worker.ts']),
    ('sw-global-state', 'warn', '^(let|var)\\s+\\w+\\s*=',
     'a mutable global in the service worker is lost when Chrome stops it (about 30 s idle) -> keep state in chrome.storage.session or chrome.storage.local', ['sw.js', 'sw.ts', 'service-worker.js', 'service-worker.ts', 'service_worker.js', 'service_worker.ts', 'background.js', 'background.ts', '*-worker.js', '*-worker.ts', '*_worker.js', '*_worker.ts']),
    ('sw-long-timer', 'warn', '\\bset(Timeout|Interval)\\([^;]*,\\s*(\\d{5,}|\\d+\\s*\\*\\s*60\\b)|^\\s*\\}\\s*,\\s*(\\d{5,}|\\d+\\s*\\*\\s*60\\b)',
     'timers die with the worker -> chrome.alarms for anything longer than a few seconds', ['sw.js', 'sw.ts', 'service-worker.js', 'service-worker.ts', 'service_worker.js', 'service_worker.ts', 'background.js', 'background.ts', '*-worker.js', '*-worker.ts', '*_worker.js', '*_worker.ts']),
    ('sw-nested-listener', 'warn', '^\\s+chrome\\.[\\w.]+\\.on[A-Z]\\w*\\.addListener\\(',
     'register event listeners synchronously at the top level of the worker, not inside a function or after an await, so Chrome can wake the worker for them', ['sw.js', 'sw.ts', 'service-worker.js', 'service-worker.ts', 'service_worker.js', 'service_worker.ts', 'background.js', 'background.ts', '*-worker.js', '*-worker.ts', '*_worker.js', '*_worker.ts']),
    ('sw-keepalive', 'warn', 'keep-?alive|setInterval\\([^,]*chrome\\.runtime\\.getPlatformInfo',
     'keep-alive hacks fight the worker lifecycle -> store state and let the worker stop', ['sw.js', 'sw.ts', 'service-worker.js', 'service-worker.ts', 'service_worker.js', 'service_worker.ts', 'background.js', 'background.ts', '*-worker.js', '*-worker.ts', '*_worker.js', '*_worker.ts']),
    ('mf-version-2', 'error', '\\"manifest_version\\"\\s*:\\s*2\\b',
     'Manifest V2 no longer runs in Chrome -> "manifest_version": 3', ['manifest.json']),
    ('mf-browser-action', 'error', '\\"(browser_action|page_action)\\"\\s*:',
     'browser_action/page_action -> "action"', ['manifest.json']),
    ('mf-background-page', 'error', '\\"(scripts|page|persistent)\\"\\s*:',
     'MV3 background is a service worker -> "background": { "service_worker": "sw.js", "type": "module" }', ['manifest.json']),
    ('mf-webrequest-blocking', 'error', '\\"webRequestBlocking\\"',
     'webRequestBlocking is MV2 only -> declarativeNetRequest', ['manifest.json']),
]
FILES = ['*.js', '*.mjs', '*.ts', '*.tsx', '*.jsx', 'manifest.json']
COMMENT = '//'
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".agents", ".claude", ".cursor", "dist", "build", "target", ".godot"}
COMPILED = [(rid, lvl, re.compile(rx), msg, globs) for rid, lvl, rx, msg, globs in RULES]


def strip_comment(line):
    """Drop a trailing comment, leaving string literals alone."""
    q = None
    i = 0
    while i < len(line):
        c = line[i]
        if q:
            if c == "\\":
                i += 2
                continue
            if c == q:
                q = None
        elif c in "\"'`":
            q = c
        elif line.startswith(COMMENT, i):
            return line[:i]
        i += 1
    return line


def wanted(name):
    return any(fnmatch.fnmatch(name, g) for g in FILES)


def walk(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
            continue
        for root, dirs, files in os.walk(p):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for f in sorted(files):
                if wanted(f):
                    yield os.path.join(root, f)


def scan(path):
    out = []
    name = os.path.basename(path)
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError as e:
        return [(path, 0, "error", "unreadable", str(e))]
    for n, raw in enumerate(lines, 1):
        code = strip_comment(raw)
        if not code.strip():
            continue
        accepted = "guard: ok" in raw  # a person accepted the warnings on this line
        for rid, lvl, rx, msg, globs in COMPILED:
            if accepted and lvl == "warn":
                continue
            if globs and not any(fnmatch.fnmatch(name, g) for g in globs):
                continue
            if rx.search(code):
                out.append((path, n, lvl, rid, msg))
    return out


def main(argv):
    if "--list" in argv:
        for rid, lvl, _, msg, globs in RULES:
            print(f"{lvl:5} [{rid}] {msg}" + (f"  (only {', '.join(globs)})" if globs else ""))
        return 0
    if any(a.startswith("-") for a in argv):
        print(__doc__)
        return 2
    paths = argv or ["."]
    for p in paths:
        if not os.path.exists(p):
            print(f"no such path: {p}", file=sys.stderr)
            return 2
    files = list(walk(paths))
    findings = []
    for f in files:
        findings.extend(scan(f))
    for path, n, lvl, rid, msg in findings:
        print(f"{os.path.relpath(path)}:{n}: {lvl} [{rid}] {msg}")
    errors = sum(1 for x in findings if x[2] == "error")
    warns = sum(1 for x in findings if x[2] == "warn")
    print(f"mv3_worker_guard: {len(files)} file(s), {errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Find Tauri 1 APIs, imports and config keys in a Tauri 2 app (front end, src-tauri Rust, tauri.conf.json, manifests).

Usage: python3 tauri2_guard.py [PATH ...]        (default: the current folder)
       python3 tauri2_guard.py --list            (print every rule)

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
    ('api-tauri-module', 'error', '[\\"\']@tauri-apps/api/tauri[\\"\']',
     '@tauri-apps/api/tauri was renamed -> @tauri-apps/api/core (invoke, convertFileSrc)', ['*.ts', '*.tsx', '*.js', '*.mjs', '*.jsx', '*.vue', '*.svelte']),
    ('api-plugin-module', 'error', '[\\"\']@tauri-apps/api/(fs|dialog|shell|http|clipboard|notification|globalShortcut|os|process|updater|cli)[\\"\']',
     'this module moved to a plugin in Tauri 2 -> @tauri-apps/plugin-<name> plus the Rust crate tauri-plugin-<name> and a capability permission', ['*.ts', '*.tsx', '*.js', '*.mjs', '*.jsx', '*.vue', '*.svelte']),
    ('app-window', 'error', '\\bappWindow\\b',
     'appWindow was removed -> getCurrentWebviewWindow() from @tauri-apps/api/webviewWindow (or getCurrentWindow() from /window)', ['*.ts', '*.tsx', '*.js', '*.mjs', '*.jsx', '*.vue', '*.svelte']),
    ('webview-window-import', 'error', 'import\\s*\\{[^}]*\\bWebviewWindow\\b[^}]*\\}\\s*from\\s*[\\"\']@tauri-apps/api/window[\\"\']',
     'WebviewWindow moved -> import it from @tauri-apps/api/webviewWindow', ['*.ts', '*.tsx', '*.js', '*.mjs', '*.jsx', '*.vue', '*.svelte']),
    ('invoke-snake-args', 'warn', 'invoke\\(\\s*[\\"\'][^\\"\']+[\\"\']\\s*,\\s*\\{[^}]*\\b[a-z0-9]+_[a-z0-9_]+\\s*:',
     'Tauri command arguments are camelCase on the JS side by default (Rust note_title -> JS noteTitle), unless the command uses rename_all = "snake_case"', ['*.ts', '*.tsx', '*.js', '*.mjs', '*.jsx', '*.vue', '*.svelte']),
    ('global-tauri', 'warn', 'window\\.__TAURI__\\b',
     'window.__TAURI__ only exists with app.withGlobalTauri: true -> import from @tauri-apps/api instead', ['*.ts', '*.tsx', '*.js', '*.mjs', '*.jsx', '*.vue', '*.svelte']),
    ('shell-open-url', 'warn', 'import\\s*\\{[^}]*\\bopen\\b[^}]*\\}\\s*from\\s*[\\"\']@tauri-apps/plugin-shell[\\"\']',
     'shell open() is deprecated for URLs and files -> openUrl / openPath from @tauri-apps/plugin-opener', ['*.ts', '*.tsx', '*.js', '*.mjs', '*.jsx', '*.vue', '*.svelte']),
    ('conf-allowlist', 'error', '\\"allowlist\\"\\s*:',
     'the allowlist was replaced by capabilities -> src-tauri/capabilities/*.json with plugin permissions', ['tauri.conf.json']),
    ('conf-tauri-key', 'error', '^\\s{0,4}\\"tauri\\"\\s*:\\s*\\{',
     'the top-level "tauri" object was renamed -> "app" (and bundle moves to the top level)', ['tauri.conf.json']),
    ('conf-dist-dir', 'error', '\\"distDir\\"\\s*:',
     'build.distDir was renamed -> build.frontendDist', ['tauri.conf.json']),
    ('conf-dev-path', 'error', '\\"devPath\\"\\s*:',
     'build.devPath was renamed -> build.devUrl', ['tauri.conf.json']),
    ('conf-package', 'error', '^\\s{0,4}\\"package\\"\\s*:\\s*\\{',
     'the "package" object was removed -> top-level productName and version', ['tauri.conf.json']),
    ('conf-system-tray', 'error', '\\"systemTray\\"\\s*:',
     'systemTray was renamed -> app.trayIcon (or build it in Rust with TrayIconBuilder)', ['tauri.conf.json']),
    ('conf-updater', 'error', '\\"updater\\"\\s*:\\s*\\{\\s*\\"active\\"',
     'the built-in updater moved to a plugin -> plugins.updater and tauri-plugin-updater', ['tauri.conf.json']),
    ('rs-get-window', 'error', '\\.get_window\\(',
     'get_window() only exists behind the unstable feature in Tauri 2 -> get_webview_window()', ['*.rs']),
    ('rs-emit-all', 'error', '\\.emit_all\\(',
     'emit_all() was removed -> emit() (to every target), or emit_to()', ['*.rs']),
    ('rs-system-tray', 'error', '\\bSystemTray(Event|Menu|MenuItem)?\\b',
     'SystemTray was replaced -> tauri::tray::TrayIconBuilder (feature tray-icon)', ['*.rs']),
    ('rs-window-builder', 'error', '\\bWindowBuilder::new\\(',
     'WindowBuilder::new was replaced -> WebviewWindowBuilder::new(app, label, WebviewUrl::App(...))', ['*.rs']),
    ('rs-custom-menu', 'error', '\\bCustomMenuItem\\b|\\bMenu::new\\(\\s*\\)',
     'the Tauri 1 menu API was replaced -> tauri::menu::{MenuBuilder, MenuItemBuilder}', ['*.rs']),
    ('rs-api-module', 'error', '\\btauri::api::',
     'tauri::api was removed -> the matching plugin crate (tauri-plugin-shell, -dialog, -fs, -http, -os, -process)', ['*.rs']),
    ('rs-path-resolver', 'error', '\\.path_resolver\\(\\)',
     'path_resolver() was removed -> app.path() (the PathResolver from the Manager trait)', ['*.rs']),
    ('rs-window-param', 'warn', 'fn\\s+\\w+\\s*\\([^)]*:\\s*tauri::Window\\b',
     'commands get a WebviewWindow in Tauri 2 -> window: tauri::WebviewWindow', ['*.rs']),
    ('cargo-tauri-1', 'error', '^\\s*tauri(-build)?\\s*=\\s*(\\{[^}]*version\\s*=\\s*)?\\"[~^=]?1\\.',
     'Cargo.toml pins Tauri 1 -> tauri = "2" and tauri-build = "2"', ['Cargo.toml']),
    ('npm-tauri-1', 'error', '\\"@tauri-apps/(api|cli)\\"\\s*:\\s*\\"[~^]?1\\.',
     'package.json pins Tauri 1 -> @tauri-apps/api and @tauri-apps/cli 2.x', ['package.json']),
]
FILES = ['*.ts', '*.tsx', '*.js', '*.mjs', '*.jsx', '*.vue', '*.svelte', '*.rs', 'tauri.conf.json', 'Cargo.toml', 'package.json']
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
    print(f"tauri2_guard: {len(files)} file(s), {errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Pattern scan of a skill, plugin or MCP server directory before install.

Usage: python3 audit_extension.py <dir> [--json]
Prints one finding per line as "severity rule path:line: message" and exits 1 if any finding is high.
Standard library only. It reads files; it never runs them. A clean result is not approval.
"""
import json
import re
import sys
from pathlib import Path

# Some patterns are assembled from pieces so this file does not match its own rules.
SH = r"(?:ba|z|da|k)?sh\b"
FETCH_ALT = r"(?:cu" + r"rl|wg" + r"et)"
FETCH = r"\b" + FETCH_ALT + r"\b"
AGENT_WORDS = r"\b(?:ign" + r"ore|disre" + r"gard|forget)\s+(?:all\s+|any\s+)?(?:previous|prior|above|earlier|system)\s+(?:instructions|prompts?|rules)\b"
KEEP_QUIET = r"\b(?:do\s+not|don't|never)\s+(?:tell|inform|show|mention\s+(?:this\s+)?to)\s+the\s+user\b|\bwithout\s+(?:asking|telling)\s+the\s+user\b"

RULES = [
    ("hidden-unicode", "high", re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff\U000e0000-\U000e007f]"),
     "Invisible or bidirectional characters can hide text from reviewers."),
    ("pipe-to-shell", "high", re.compile(FETCH + r"[^\n|]*\|\s*(?:sudo\s+)?" + SH, re.I), "Pipes a download into a shell."),
    ("eval-remote", "high", re.compile(r"(?:\beval|\bsource|\b(?:ba)?sh\s+-c)\s*[\"']?\$\(\s*" + FETCH), "Runs downloaded text."),
    ("base64-exec", "high", re.compile(r"base64\s+(?:-d|--decode)\b[^\n]*\|\s*(?:sudo\s+)?" + SH + r"|b64decode\([^\n]*\)[^\n]*\b(?:exec|eval)\b|\b(?:exec|eval)\([^\n]*b64decode", re.I),
     "Decodes and runs hidden code."),
    ("credential-access", "high", re.compile(r"(?:~|\$HOME|expanduser\([\"']~)[\\/]\." + r"(?:ssh|aws|gnupg|kube|docker|netrc)\b|\.aws/cred" + r"entials|\bid_(?:rsa|ed25519)\b|Login" + r" Data|\.config/g" + r"cloud", re.I),
     "Touches credential files or browser profiles."),
    ("env-exfiltration", "high", re.compile(r"\b(?:env|printenv)\b\s*\|\s*(?:" + FETCH_ALT[3:-1] + r"|nc)\b|os\.environ[^\n]*(?:requests\.|urlopen|http)|process\.env[^\n]*fetch\(", re.I),
     "Sends environment variables over the network."),
    ("agent-directed-wording", "high", re.compile(AGENT_WORDS + "|" + KEEP_QUIET, re.I), "Wording aimed at steering the agent or hiding actions from the user."),
    ("auto-approve", "medium", re.compile(r"--dangerously-skip-" + r"permissions|--yo" + r"lo\b|\"(?:autoApprove|alwaysAllow)\"\s*:\s*\[", re.I), "Turns off permission prompts."),
    ("unpinned-npx", "medium", re.compile(r"\bnpx\s+(?:-y\s+|--yes\s+)?(@?[\w./-]+?)(?:@latest)?(?=[\s\"',\]]|$)"), "Unpinned package (npx); use an exact version."),
    ("unpinned-uvx", "medium", re.compile(r"\buvx\s+(?!--from\b)([A-Za-z][\w.-]*)(?=[\s\"',\]]|$)"), "Unpinned package (uvx); use ==version."),
    ("plain-http-url", "medium", re.compile(r"\bhttp://(?!localhost|127\.0\.0\.1|\[::1\])[^\s\"'<>)]+"), "Plain HTTP URL; traffic can be altered in transit."),
    ("raw-ip-url", "medium", re.compile(r"\bhttps?://(?:\d{1,3}\.){3}\d{1,3}"), "Network call to a bare IP address."),
    ("encoded-blob", "medium", re.compile(r"[A-Za-z0-9+/]{200,}={0,2}"), "Long encoded string nobody can review."),
    ("html-comment", "medium", re.compile(r"<!--(?!\s*(?:snippet|/snippet|prettier|markdownlint))"), "HTML comment in Markdown is invisible when rendered; read it."),
    ("network-call", "info", re.compile(FETCH + r"|\bfetch\(|requests\.(?:get|post)|urlopen\(|\bInvoke-WebRequest\b"), "Makes a network call; check the host."),
]
HOOK_FILES = re.compile(r"(?:^|/)(?:hooks/hooks\.json|hooks\.json|settings\.json|plugin\.json)$")
TEXT_EXT = {".md", ".mdc", ".txt", ".json", ".yaml", ".yml", ".toml", ".sh", ".bash", ".zsh", ".ps1", ".py", ".js", ".mjs", ".cjs", ".ts", ".rb", ".go", ""}
PINNED_NPX = re.compile(r"@\d+\.\d+\.\d+")


MCP_FILES = re.compile(r"(?:^|/)(?:\.mcp\.json|mcp\.json|mcp_config\.json|settings\.json|plugin\.json)$")


def check_mcp_config(rel, text):
    """Check command + args pairs in MCP config files, where the package name sits in args."""
    out = []
    try:
        data = json.loads(text)
    except ValueError:
        return out
    servers = data.get("mcpServers") if isinstance(data, dict) else None
    if not isinstance(servers, dict):
        return out
    for name, cfg in servers.items():
        if not isinstance(cfg, dict):
            continue
        cmd = str(cfg.get("command", ""))
        args = [str(a) for a in cfg.get("args", []) if isinstance(a, (str, int))]
        pkgs = [a for a in args if not a.startswith("-") and not a.startswith(".") and not a.startswith("/")]
        pkg = pkgs[0] if pkgs else ""
        if cmd.endswith("npx") and pkg and not PINNED_NPX.search(pkg):
            out.append(("medium", "unpinned-npx", rel, None, f"MCP server {name}: {pkg} has no exact version."))
        if cmd.endswith("uvx") and pkg and "==" not in pkg and "--from" not in args:
            out.append(("medium", "unpinned-uvx", rel, None, f"MCP server {name}: {pkg} has no ==version."))
        url = str(cfg.get("url") or cfg.get("serverUrl") or cfg.get("httpUrl") or "")
        if url.startswith("http:" + "//") and not re.match(r"http:/" r"/(?:localhost|127\.0\.0\.1)", url):
            out.append(("medium", "plain-http-url", rel, None, f"MCP server {name} uses plain HTTP."))
    return out


def scan_file(root, path):
    rel = path.relative_to(root).as_posix()
    findings = []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return [("medium", "binary-file", rel, None, "Binary or unreadable file; ask why a skill needs it.")]
    if HOOK_FILES.search(rel) and re.search(r"\"hooks\"\s*:", text):
        findings.append(("medium", "hooks", rel, None, "Declares hooks that run automatically; read every command."))
    if MCP_FILES.search(rel):
        findings.extend(check_mcp_config(rel, text))
    for n, line in enumerate(text.splitlines(), 1):
        for rule, sev, rx, msg in RULES:
            m = rx.search(line)
            if not m:
                continue
            if rule == "unpinned-npx" and PINNED_NPX.search(m.group(0)):
                continue
            if rule == "html-comment" and not rel.endswith((".md", ".mdc")):
                continue
            findings.append((sev, rule, rel, n, msg))
    return findings


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 2
    root = Path(argv[1]).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}")
        return 2
    findings = []
    for p in sorted(root.rglob("*")):
        if p.is_symlink():
            findings.append(("high", "symlink", p.relative_to(root).as_posix(), None, "Symlink can point outside the extension."))
        elif p.is_file() and ".git" not in p.parts and p.suffix.lower() in TEXT_EXT:
            findings.extend(scan_file(root, p))
        elif p.is_file() and ".git" not in p.parts:
            findings.append(("info", "other-file", p.relative_to(root).as_posix(), None, "Not scanned; check it by hand."))
    order = {"high": 0, "medium": 1, "info": 2}
    findings.sort(key=lambda f: (order[f[0]], f[2], f[3] or 0))
    if "--json" in argv:
        print(json.dumps([dict(zip(("severity", "rule", "file", "line", "message"), f)) for f in findings], indent=2))
    else:
        for sev, rule, rel, line, msg in findings:
            print(f"{sev} {rule} {rel}{':' + str(line) if line else ''}: {msg}")
        counts = {s: sum(1 for f in findings if f[0] == s) for s in order}
        print(f"summary: {counts['high']} high, {counts['medium']} medium, {counts['info']} info")
    return 1 if any(f[0] == "high" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

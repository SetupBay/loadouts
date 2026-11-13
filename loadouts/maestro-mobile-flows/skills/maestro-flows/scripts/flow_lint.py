# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml==6.0.3"]
# ///
"""Lint Maestro flow files before they reach a device.

Usage: uv run flow_lint.py [.maestro]      (default directory: .maestro)

Errors (exit 1): unknown commands (typos), a missing appId header, a runFlow file that does not exist,
a top-level flow with no assertion, a bare assertScreenshot, a literal value typed into a password, PIN,
OTP or token field (use ${VAR} and pass it with -e).
Warnings: tapOn by screen coordinates, no tags (cannot filter smoke runs), variables the flow needs from -e.
Read-only.
"""
import re
import sys
from pathlib import Path

import yaml

COMMANDS = set("""tapOn doubleTapOn longPressOn assertVisible assertNotVisible assertTrue assertNoDefectsWithAI
assertScreenshot assertWithAI extractTextWithAI back clearKeychain hideKeyboard pasteText scroll inputText
inputRandomText inputRandomNumber inputRandomEmail inputRandomPersonName inputRandomCityName inputRandomCountryName
inputRandomColorName launchApp setPermissions swipe openLink pressKey eraseText takeScreenshot extendedWaitUntil
stopApp killApp clearState runFlow setLocation setOrientation repeat copyTextFrom setClipboard runScript
waitForAnimationToEnd evalScript scrollUntilVisible travel startRecording stopRecording addMedia setAirplaneMode
toggleAirplaneMode setDarkMode toggleDarkMode assertDarkMode assertLightMode retry""".split())
ASSERTS = {"assertVisible", "assertNotVisible", "assertTrue", "assertScreenshot", "assertWithAI",
           "assertNoDefectsWithAI", "assertDarkMode", "assertLightMode", "extendedWaitUntil"}
SECRET_FIELD = re.compile(r"pass|pin\b|otp|token|secret|cvv|card.?number", re.I)
VAR = re.compile(r"\$\{(\w+)\}")
NESTED = ("commands",)  # repeat / retry / runFlow-inline bodies


def load(path):
    docs = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    if len(docs) == 1:
        return {}, docs[0] or []
    return docs[0] or {}, docs[1] or []


def walk(commands):
    """Yield (name, value) for every command, including nested repeat/retry/runFlow bodies."""
    for item in commands or []:
        if isinstance(item, str):
            yield item, None
        elif isinstance(item, dict):
            for name, value in item.items():
                yield name, value
                if isinstance(value, dict):
                    for key in NESTED:
                        if isinstance(value.get(key), list):
                            yield from walk(value[key])


def selector_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(str(value.get(k, "")) for k in ("id", "text", "label"))
    return ""


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".maestro")
    flows = sorted(p for p in root.rglob("*.y*ml") if p.suffix in (".yaml", ".yml") and p.name != "config.yaml")
    if not flows:
        print(f"no flows under {root}/")
        return 1
    subflows = set()
    parsed = {}
    errors = warnings = 0

    def report(kind, path, msg):
        nonlocal errors, warnings
        if kind == "fix":
            errors += 1
        else:
            warnings += 1
        print(f"{kind:<4} {path.relative_to(root)}: {msg}")

    for p in flows:
        try:
            parsed[p] = load(p)
        except yaml.YAMLError as e:
            report("fix", p, f"YAML does not parse: {str(e).splitlines()[0]}")
            continue
        for name, value in walk(parsed[p][1]):
            if name == "runFlow":
                target = value if isinstance(value, str) else (value or {}).get("file")
                if target:
                    t = (p.parent / target).resolve()
                    subflows.add(t)
                    if not t.exists():
                        report("fix", p, f"runFlow file not found: {target}")

    for p, (header, commands) in parsed.items():
        is_sub = p.resolve() in subflows or "subflows" in p.parts
        if not isinstance(header, dict) or not header.get("appId"):
            report("fix", p, "missing appId in the header (appId: com.example.app, then ---)")
        names, last_field, needed = [], "", set()
        defined = set((header or {}).get("env", {}) or {}) if isinstance(header, dict) else set()
        for name, value in walk(commands):
            names.append(name)
            if name not in COMMANDS:
                report("fix", p, f"unknown command '{name}' (typo? see the cheat_sheet MCP tool)")
            if name == "assertScreenshot" and not value:
                report("fix", p, "assertScreenshot needs a name, e.g. assertScreenshot: home_screen")
            if name in ("tapOn", "doubleTapOn", "longPressOn"):
                if isinstance(value, dict) and "point" in value:
                    report("warn", p, f"{name} by screen coordinates ({value['point']}) breaks on other screen sizes; use id or text")
                last_field = selector_text(value)
            if name == "inputText":
                text = str(value if not isinstance(value, dict) else value.get("text", ""))
                if SECRET_FIELD.search(last_field) and not VAR.fullmatch(text.strip()):
                    report("fix", p, f"literal value typed into '{last_field.strip()}': use ${{VAR}} and pass it with -e")
            for v in VAR.findall(yaml.safe_dump(value) if value is not None else ""):
                if v not in defined:
                    needed.add(v)
        if not is_sub and not ASSERTS.intersection(names):
            report("fix", p, "no assertion: a flow that only taps proves nothing (add assertVisible or similar)")
        if not is_sub and not (header or {}).get("tags"):
            report("warn", p, "no tags: add e.g. tags: [smoke] so runs can use --include-tags")
        if needed:
            report("warn", p, "needs " + " ".join(f"-e {v}=..." for v in sorted(needed)))

    top = len([p for p in parsed if p.resolve() not in subflows and "subflows" not in p.parts])
    print(f"flows: {top} top-level, {len(parsed) - top} subflows; {errors} errors, {warnings} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

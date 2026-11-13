---
name: maestro-flows
description: Write, run and debug Maestro UI flows for iOS and Android apps (React Native, Flutter, native) with the Maestro MCP server and CLI, and lint flows before they hit a device. Use when the user wants an end-to-end or smoke test of a mobile app, a flow in .maestro/ fails, or a screen needs checking after a change.
---

# Maestro flows for mobile apps

Maestro drives a simulator, emulator or device from YAML flows. The `maestro` MCP server (started by the Maestro
CLI 2.11 or later with `maestro mcp`) lets you look at the screen and run commands while you write the flow.

## Rules first
- Use a simulator or emulator, or a device the human named. If `list_devices` shows nothing running, ask the human
  to start one; do not boot or wipe devices yourself.
- Never type real credentials. Flows use `${TEST_EMAIL}`-style variables passed with `-e`, from a test account.
- Cloud runs upload the app and may cost money: only on request.

## Write a flow
1. `inspect_screen` to see the current view hierarchy before guessing selectors. `cheat_sheet` for syntax.
2. Try commands one at a time with the `run` tool's inline `yaml` (for example `- tapOn: {id: sign_in_button}`),
   then put the working steps into `.maestro/<name>.yaml`.
3. Shape (see `references/login.yaml.txt` and `references/sign-in.yaml.txt`; drop the .txt when copying):
   - Header with `appId`, a `name` and `tags` (`smoke` for the quick set), then `---`.
   - `launchApp: {clearState: true}` so each flow starts clean and flows can run in any order.
   - Select by accessibility id (`testID` in React Native, `Modifier.testTag`/`Key` elsewhere) over visible text,
     and never by screen coordinates. Ask to add an id when there is none.
   - Shared steps (sign-in, onboarding) go in `.maestro/subflows/` and are called with `runFlow`.
   - End with assertions on what the user should see (`assertVisible`, `assertNotVisible`). Maestro waits for
     elements automatically; use `extendedWaitUntil` for slow screens instead of adding sleeps.

## Check before running
```bash
uv run .agents/skills/maestro-flows/scripts/flow_lint.py .maestro
```
(Claude Code: `.claude/skills/...`.) It fails on unknown commands, missing `appId`, missing `runFlow` files, flows
without an assertion, a bare `assertScreenshot`, and literal values typed into password, PIN, OTP or token fields.
It lists the `-e` variables each flow needs.

## Run
- One flow while working: the MCP `run` tool with `files`, or `maestro test .maestro/login.yaml -e TEST_EMAIL=... -e TEST_PASSWORD=...`.
- The smoke set: `maestro test .maestro --include-tags smoke`.
- For CI and reports: `maestro test .maestro --format junit --output maestro-report.xml --test-output-dir maestro-out`.
On failure, read the report and screenshots in the output folder, `inspect_screen` at the failing step, and fix the
selector or the app, not the assertion. Do not delete or weaken an assertion to get green; say so if you think one
is wrong.

## Done means
The lint passes, the flows pass on the named device, and the summary lists the flows run, the device, and any flow
not run (and why).

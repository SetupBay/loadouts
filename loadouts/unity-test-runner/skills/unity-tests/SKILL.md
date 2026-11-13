---
name: unity-tests
description: Run Unity Test Framework Edit Mode and Play Mode tests from the command line and read the NUnit results, including the zero-tests case Unity reports as success. Use after changing C# in a Unity project, when adding tests, or when the user asks whether the Unity tests pass.
---

# Unity tests from the command line

The Unity agent plugin can edit scripts and scenes; this skill is how you prove the C# still works. It runs the
Unity Test Framework headless and reads the result file, because the exit code alone is misleading:

| Exit | Meaning |
|---|---|
| 0 | every test passed **or no tests ran at all** (a filter that matches nothing, a missing test assembly) |
| 2 | one or more tests failed |
| 3 | run error: usually a compile error, so no tests ran |
| 4 | the test platform isn't installed |

## 1. Preconditions
- `ProjectSettings/ProjectVersion.txt` gives the Editor version. `UNITY_PATH` must point at that Editor's binary.
  If it isn't set, ask the human for the path; do not guess another version (it would re-import the project).
- **The project must not be open in the Editor.** Batch mode refuses a project that is already open. If the human
  has it open, ask them to close it, or to run the tests in Window → General → Test Runner and paste the result.
- `git status` clean, or the human knows you are about to run a re-import.

## 2. Edit Mode first
Edit Mode tests run plain C# without entering Play mode, in seconds. Put logic in plain classes so it can be tested
here, and keep MonoBehaviours thin.
- Test assembly: `Assets/Tests/EditMode/` with an `.asmdef` like `references/EditModeTests.asmdef.json`
  (Editor-only, references `UnityEngine.TestRunner` and `UnityEditor.TestRunner`, `nunit.framework.dll`, and the
  runtime assembly under test, constrained to `UNITY_INCLUDE_TESTS`). Save it with the `.asmdef` extension.
- Example test: `references/HealthTests.cs`. NUnit `[Test]` and `[TestCase]`; `Assert.That(x, Is.EqualTo(y))`.
- Play Mode tests (`[UnityTest]` coroutines, scenes, physics) go in `Assets/Tests/PlayMode/` with a separate
  `.asmdef` that is not Editor-only. Use them for behaviour that needs frames.

## 3. Run
```bash
python3 .agents/skills/unity-tests/scripts/unity_tests.py run --platform EditMode
python3 .agents/skills/unity-tests/scripts/unity_tests.py run --platform EditMode --filter "Game.Tests.HealthTests"
python3 .agents/skills/unity-tests/scripts/unity_tests.py run --platform PlayMode
```
(Claude Code installs the skill under `.claude/skills/`.) It writes `TestResults/<platform>.xml` and `.log`
(add `TestResults/` to `.gitignore`), deletes old ones first so a stale file is never read, prints the Unity
command, each failing test with its message and first stack line, compile errors from the log, and skipped tests
with their reasons. Already have a results file? `unity_tests.py read TestResults/editmode.xml`.

## 4. Read it like a reviewer
- `NO TESTS RAN` is a failure, whatever Unity's exit code says. Fix the filter, the `.asmdef` or the platform.
- `COMPILE` lines: fix those first; nothing else ran.
- Never mark a test `[Ignore]`, delete it, or loosen an assertion to get green. If a test is wrong, say why and ask.
- Report the summary line (total, passed, failed, skipped) and the command you ran.

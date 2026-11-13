# Godot 4 headless tests

This project's game rules are checked by GDScript tests that run in Godot's headless mode, with no
editor and no window. Run them after every change and before you say a change is done. A script that
parses can still be wrong: signal timing, freed nodes and off-by-one damage all parse fine.

## Commands

```bash
godot --headless --import --path .            # once per fresh clone or new class_name; builds .godot/
godot --headless --path . --script res://tests/run_tests.gd   # runs every test, exit 1 on any failure
python3 .agents/skills/godot-headless-tests/scripts/gd_test_lint.py tests   # catches tests that can't fail
```

Use the Godot 4 binary the project pins (`config/features` in project.godot). If it isn't on PATH,
ask for its path rather than downloading one. Wrap the run in `timeout 300` in CI so a hung test fails.

## Layout

- `tests/run_tests.gd`: the runner (copy it from the skill's `references/run_tests.gd`). It extends
  SceneTree, finds `tests/test_*.gd`, runs every `test_*()` method, prints `PASS`/`FAIL` per test
  and quits with exit code 1 if anything failed.
- `tests/test_<thing>.gd`: one suite per script or scene. A suite `extends RefCounted` and declares
  `var t: SceneTree`; the runner sets `t` to itself before each test.
- Optional `before_each()` and `after_each()` run around every test; they may `await`.

## Writing tests

- Check with `t.equal(actual, expected, "label")` and `t.check(condition, "message")`. Every test
  needs at least one. `print()` is not a check.
- A script error inside a test (calling a method on null, a bad cast) marks that test as failed. The
  runner hooks Godot's Logger for this, because otherwise Godot only prints the error and the test
  looks like a pass. Don't "fix" a failing test by guarding the null; find out why it was null.
- Add nodes under `t.root`, never `get_tree()` (a RefCounted suite isn't in the tree). Free what you
  add in `after_each()`.
- Scene tests: `load("res://scenes/x.tscn").instantiate()`, add to `t.root`, then
  `await t.frames(1)` so `_ready()` and the first process frame have run. `queue_free()` only happens
  at the end of a frame, so await a frame before you check a node is gone.
- Always `await t.frames(n)`. Never `OS.delay_msec()`, which blocks the main loop so nothing moves,
  and avoid `create_timer()` waits: call the timeout handler, or set the Timer's `wait_time` tiny.
- Seed randomness: pass a `RandomNumberGenerator` with a fixed `seed` into the code under test.
- Never call `quit()` from a test. The runner owns the exit code.
- Autoloads from project.godot are loaded in a `--script` run (Godot 4.7) and live for the whole
  run, so state leaks between tests. Reset whatever a test changes in `before_each()`.
- Editor-only code (EditorInterface, EditorPlugin) can't be exercised here. Keep plugin UI thin.

If the project already uses GUT or gdUnit4, use that instead and keep these rules for the tests.

## Done means

1. `--import` has run since the last new `class_name`, or the run fails with "Could not find type".
2. The lint script reports 0 errors on `tests/`.
3. The run ends with `0 failed` and exits 0. Add or change a test for every rule you change, and
   say which test covers it.
4. List anything that still needs a human play-test (feel, visuals, audio, input devices).

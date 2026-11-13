---
name: godot-headless-tests
description: Set up and run GDScript tests for a Godot 4 project in headless mode, with a SceneTree runner that fails on script errors and exits non-zero. Use when adding a test, changing game rules, or before saying a Godot change is done.
---

# Godot 4 headless tests

## 1. Set up once

If `tests/run_tests.gd` doesn't exist, copy `references/run_tests.gd` from this skill to
`tests/run_tests.gd`. It needs Godot 4.5 or later (it uses the `Logger` class); check
`config/features` in project.godot. Then build the import cache:

```bash
godot --headless --import --path .
```

Run `--import` again whenever you add a `class_name` or a new resource. Without it a fresh clone
fails with `Parse Error: Could not find type "Health"` even though the code is fine.

## 2. Write the test

One suite per script or scene, in `tests/test_<thing>.gd`:

```gdscript
extends RefCounted

var t: SceneTree   # set by the runner
var health: Health


func before_each() -> void:
	health = Health.new()
	health.maximum = 50
	t.root.add_child(health)   # runs _ready()


func after_each() -> void:
	health.free()


func test_damage_clamps_at_zero_and_emits_died_once() -> void:
	var deaths := [0]
	health.died.connect(func() -> void: deaths[0] += 1)
	health.damage(80)
	health.damage(10)
	t.equal(health.current, 0)
	t.equal(deaths[0], 1, "died emitted")
```

For a scene, instance it, add it under `t.root`, then `await t.frames(1)` before you poke it.
After `queue_free()`, `await t.frames(1)` before checking the node has gone. Capture signal counts
in an array (lambdas capture by value, so a plain `int` won't update).

## 3. Lint the tests

```bash
python3 scripts/gd_test_lint.py tests
```

Errors: a test with no check, `get_tree()` in a suite, `OS.delay_msec()`, `t.frames()` without
`await`, `quit()` in a test, editor-only APIs. Warnings: `create_timer()` waits, unseeded random
calls, `print()` used as a check, bare `assert()`. Fix errors; fix or justify warnings
(`# lint: ok` on the line). Try it on `references/bad-test-sample.gd.txt` (7 errors, 4 warnings).

## 4. Run

```bash
timeout 300 godot --headless --path . --script res://tests/run_tests.gd
```

Each test prints `PASS suite::test_name` or `FAIL suite::test_name: reason`, then
`N passed, M failed`. Exit code 1 means at least one failure. A script error inside a test is a
failure with the message and line, such as `script error: Cannot call method 'get_name' on a null
value. (test_arena.gd:14)`. A suite that doesn't parse shows as `FAIL test_x.gd: script did not
load`.

## 5. Report

Give the last line of the run, the tests you added or changed and which rule each covers, and
anything left for a human play-test.

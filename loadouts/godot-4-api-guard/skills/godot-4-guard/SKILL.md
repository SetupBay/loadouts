---
name: godot-4-guard
description: Check GDScript for Godot 3 syntax and renamed APIs before saying a Godot 4 change is done. Use after writing or editing any .gd file, when Godot reports a parse error, or when porting Godot 3 code, tutorials or snippets into a Godot 4 project.
---

# Godot 4 guard

Models trained on years of Godot 3 tutorials still write `yield`, `export var`, `onready`, `KinematicBody2D` and
`move_and_slide(velocity)` into Godot 4 projects. Godot 4 refuses to parse most of it, but its parser stops at the
first error, so fixing one line at a time wastes runs. This skill finds them all at once, then lets Godot itself confirm.

## 1. Confirm the project is Godot 4
- `project.godot` must contain `config_version=5`. If it says `config_version=4`, this is a Godot 3 project:
  stop and tell the human. Porting a whole project is the editor's job (Project → Tools → Upgrade Project), after a commit.
- `godot --version` should print `4.x`. If `godot` is not on the PATH, ask where the Godot 4 binary is.

## 2. Scan for Godot 3 code
```bash
python3 .agents/skills/godot-4-guard/scripts/gd3_guard.py scenes autoload
```
(Use the path the skill was installed to: `.claude/skills/...` for Claude Code, `.agents/skills/...` for the others.
With no arguments it scans the whole project, skipping `.godot/`, `addons/` and agent folders.)

- Every `error` line is Godot 3 code. Fix each one with the replacement the line gives. `references/rename-table.md`
  has the full table with examples.
- `warn` lines are style: `emit_signal("x")` still works but `x.emit()` is the Godot 4 form; untyped functions
  should get `-> void` or a return type; `TileMap` is deprecated since 4.3 in favour of `TileMapLayer`.
- Run it again until it prints `0 error(s)`.

## 3. Let Godot check every changed script
```bash
godot --headless --path . --check-only --script res://scenes/player/player.gd
```
- Run it for each `.gd` file you changed. Any `SCRIPT ERROR` or `Parse Error` line means the script does not load,
  whatever the exit code says.
- If it complains about an unknown `class_name`, run `godot --headless --path . --import` once so the global class
  cache exists, then check again.
- `--check-only` does not load autoloads. A script that names one (`GameState.score = 10`) reports
  `Identifier not found: GameState` even though the game runs. For those scripts, the headless run below is the check.
- Then run the project briefly: `godot --headless --path . --quit-after 300` and read the output for errors.

## 4. Fixes that need care
- **`move_and_slide`**: `CharacterBody2D` already has `velocity` and `up_direction`. Delete any `var velocity`
  you added (it now clashes with the built-in), set `velocity`, call `move_and_slide()` with no arguments.
- **`yield` with a function state**: `await some_function()` waits for a coroutine; `await signal` waits for a signal.
- **`setget`**: move the setter into the property (`var hp: int = 3: set = set_hp`). In Godot 4 the setter also
  runs when the class assigns `hp` itself (Godot 3 skipped it without `self.`), so check code that relied on that.
  Inside an inline `set(value):` block, `hp = value` stores the value directly without calling the setter again.
- **Scenes (`.tscn`)**: never rewrite a Godot 3 scene by hand. Ask the human to open it in the Godot 4 editor.

## 5. Report
Say how many Godot 3 lines you replaced, which files, and that the guard and `--check-only` were clean. If something
could only be checked by playing (input feel, physics), say what the human should try.

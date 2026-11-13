# AGENTS.md: Godot 4 game jam

This is a Godot 4 project made for a game jam. Finishing beats polish. Polish beats features.

## Jam rules (follow these over any instinct to add things)
1. **Core loop first.** Until the game can be started, played, won or lost, and restarted, only work on that.
2. **Keep a cut list.** When the human asks for something big, offer the smallest version that sells the idea,
   and add the rest to `CUTLIST.md` instead of building it.
3. **Feature freeze** when the human says so (default: 75% of the way through the jam). After that: bugs,
   juice (screen shake, sound, particles), menus, and the build. Nothing new.
4. **Ship a build early.** Get a web export on itch.io (draft page) on day one so the final upload is boring.
5. Never refactor working code in the last few hours unless it fixes a crash.

## Project layout
```
scenes/       one folder per thing: player/, enemies/, ui/, levels/ (each .tscn next to its .gd)
autoload/     global singletons (GameState, Audio) — keep these few and small
assets/       art/, audio/, fonts/ — imported files, never edited by code
```
- Commit `.tscn`, `.tres`, `.gd`, `project.godot`, `export_presets.cfg` and the `*.uid` / `*.import` files.
  Ignore `.godot/` and build output.

## GDScript conventions (Godot 4)
- Static typing everywhere: `var speed: float = 200.0`, `func take_damage(amount: int) -> void:`.
  Use `:=` when the type is obvious.
- `snake_case` for files, functions and variables; `PascalCase` for `class_name` and nodes; `UPPER_SNAKE` for constants.
- Use `@export` for tunable values so the human can tweak them in the inspector instead of asking you.
- Use `@onready var sprite: Sprite2D = $Sprite2D` for child references. No `get_node()` with long paths across the tree.
- Signals for "something happened" (`signal died`, `health_changed.emit(hp)`), direct calls for "do this".
  Children signal up; parents call down.
- Connect signals in code with callables: `button.pressed.connect(_on_start_pressed)`.
- Physics and movement in `_physics_process(delta)`; visuals and input polling in `_process(delta)` or `_unhandled_input`.
- Use groups (`add_to_group("enemies")`) instead of searching the tree.
- Use `await get_tree().create_timer(0.5).timeout` for simple delays; `Tween` (`create_tween()`) for movement and juice.
- Godot 3 syntax is wrong here: no `onready`, `export`, `yield`, `KinematicBody2D`, or `connect("signal", self, "method")`.

## Editing scenes
- Prefer creating nodes in the editor (tell the human what to add) or in code. If you must edit a `.tscn` by hand,
  keep `ext_resource` ids consistent and do not reorder sections.
- Input actions belong in Project Settings → Input Map (`project.godot`), never hard-coded key codes.

## Before you say "done"
- Run the project headless to catch script errors: `godot --headless --quit` (or ask the human to press F5).
- Say what the human should test by hand, in one or two lines.

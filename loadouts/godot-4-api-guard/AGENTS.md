# AGENTS.md: Godot 4 project (Godot 3 guard)

This is a **Godot 4** project. Much of what you remember about Godot is Godot 3, and Godot 4 does not parse it.
Treat every GDScript line you write as suspect until the guard and Godot have both checked it.

## Version facts
- Engine: Godot 4.x (see `project.godot`: `config_version=5`; the 4.x minor is in `config/features`).
- GDScript 2.0: annotations (`@export`, `@onready`, `@tool`, `@rpc`), `await`, first-class signals and callables,
  typed arrays (`Array[Node]`), property setters/getters inline.
- If you are not sure an API exists in Godot 4, look it up in the class reference for this version
  (https://docs.godotengine.org/en/stable/classes/) instead of guessing. Do not copy Godot 3 tutorials or answers.

## Rules
- Write Godot 4 only. The `godot-4-guard` skill has the full Godot 3 → 4 rename table; the common traps are:
  `@export`/`@onready`/`@tool` (not keywords), `await` (not `yield`), `CharacterBody2D` (not `KinematicBody2D`),
  `instantiate()`, `is_empty()`, `deg_to_rad`, `randf_range`, `snapped`, `change_scene_to_file`, `Time.get_ticks_msec()`.
- Static types everywhere: `var speed: float = 200.0`, `func hit(amount: int) -> void:`.
- `CharacterBody2D`/`3D` have a built-in `velocity`. Do not declare your own; call `move_and_slide()` with no arguments.
- Signals: `signal died`, `died.emit()`, `button.pressed.connect(_on_pressed)`.
- Never hand-edit `.tscn` or `.tres` files saved by Godot 3 (`format=2`), and never edit `.godot/`.
- Never run the project upgrade tool or convert a Godot 3 project yourself. Ask the human, after a commit.

## Before you say "done"
1. Run the `godot-4-guard` scanner on the folders you touched; it must report `0 error(s)`.
2. Run `godot --headless --path . --check-only --script res://<file>.gd` for every changed script; no `SCRIPT ERROR`.
3. Run the project headless for a few seconds (`godot --headless --path . --quit-after 300`) and read the output.
4. Tell the human what to try by hand (controls, feel) in one or two lines.

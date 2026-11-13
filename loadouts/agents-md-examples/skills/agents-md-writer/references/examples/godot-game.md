# AGENTS.md

A 2D platformer in **Godot 4.7** (GDScript 2.0). Not Godot 3: no `yield`, `export var`, `onready`, `KinematicBody2D`.

## Commands
- Check one script: `godot --headless --path . --check-only --script res://scenes/player/player.gd`
- Run headless for errors: `godot --headless --path . --quit-after 300`
- Tests (GUT): `godot --headless --path . -s addons/gut/gut_cmdln.gd -gexit`

## Layout
- `scenes/<thing>/` with the `.tscn` next to its `.gd`; `autoload/` for the few global singletons; `assets/` imported files

## Conventions
- Static types everywhere; `@export` for values a designer tunes; signals up, calls down
- Input actions from the Input Map (`move_left`, `jump`), never raw key codes

## Never
- Hand-edit `.tscn` files beyond small property changes; never edit `.godot/`
- Add plugins to `addons/` without asking

## Done means
No `SCRIPT ERROR` from `--check-only` or the headless run, tests pass, and you told the human what to try in the game.

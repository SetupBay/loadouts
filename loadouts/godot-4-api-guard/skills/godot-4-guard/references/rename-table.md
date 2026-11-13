# Godot 3 → Godot 4: what agents get wrong most

Sources: the official "Upgrading from Godot 3 to Godot 4" guide and the engine's own rename map
(`editor/project_upgrade/renames_map_3_to_4.cpp`). The guard script checks every row marked ✓.

## GDScript syntax

| Godot 3 | Godot 4 | ✓ |
|---|---|---|
| `tool` | `@tool` | ✓ |
| `export var x = 1`, `export(int) var x` | `@export var x: int = 1`, `@export_range(0, 10) var x: int` | ✓ |
| `onready var s = $Sprite` | `@onready var s: Sprite2D = $Sprite2D` | ✓ |
| `yield(obj, "signal")` | `await obj.signal` | ✓ |
| `yield(get_tree().create_timer(1), "timeout")` | `await get_tree().create_timer(1.0).timeout` | ✓ |
| `var hp setget set_hp, get_hp` | `var hp: int: set = set_hp, get = get_hp` (or inline `set(value):`) | ✓ |
| `connect("pressed", self, "_on_pressed")` | `pressed.connect(_on_pressed)` | ✓ |
| `emit_signal("died")` | `died.emit()` (the old form still works; warning only) | ✓ |
| `remote func`, `master func`, `puppet func` | `@rpc("any_peer")`, `@rpc("authority")` | ✓ |
| `funcref(obj, "m")` | `Callable(obj, "m")` or `obj.m` | ✓ |

## Nodes and classes

| Godot 3 | Godot 4 | ✓ |
|---|---|---|
| `KinematicBody2D`, `KinematicBody` | `CharacterBody2D`, `CharacterBody3D` | ✓ |
| `Spatial`, `SpatialMaterial` | `Node3D`, `StandardMaterial3D` | ✓ |
| `Position2D` / `Position3D` | `Marker2D` / `Marker3D` | ✓ |
| `VisibilityNotifier2D` | `VisibleOnScreenNotifier2D` | ✓ |
| `YSort` | any `CanvasItem` with `y_sort_enabled = true` | ✓ |
| `Navigation2D` | `NavigationAgent2D` + `NavigationRegion2D` | ✓ |
| `Particles2D` | `GPUParticles2D` (or `CPUParticles2D`) | ✓ |
| `Tween` node, `interpolate_property` | `create_tween().tween_property(node, "position", to, 0.3)` | ✓ |
| `File.new()`, `Directory.new()` | `FileAccess.open(path, FileAccess.READ)`, `DirAccess.open(path)` | ✓ |
| `PoolStringArray`, `PoolRealArray`, ... | `PackedStringArray`, `PackedFloat32Array`, ... | ✓ |
| `TileMap` (4.0–4.2) | `TileMapLayer`, one node per layer (TileMap deprecated in 4.3) | warn |

## Methods and properties

| Godot 3 | Godot 4 | ✓ |
|---|---|---|
| `move_and_slide(velocity, Vector2.UP)` | set `velocity` (built in) and `up_direction`, then `move_and_slide()` | ✓ |
| `scene.instance()` | `scene.instantiate()` | ✓ |
| `array.empty()` | `array.is_empty()` | ✓ |
| `deg2rad`, `rad2deg` | `deg_to_rad`, `rad_to_deg` | ✓ |
| `rand_range(a, b)` | `randf_range(a, b)` / `randi_range(a, b)` | ✓ |
| `stepify(x, s)` | `snapped(x, s)` | ✓ |
| `str2var`, `var2str` | `str_to_var`, `var_to_str` | ✓ |
| `a.linear_interpolate(b, t)` | `a.lerp(b, t)` | ✓ |
| `get_tree().change_scene(path)` | `get_tree().change_scene_to_file(path)` | ✓ |
| `change_scene_to(packed)` | `change_scene_to_packed(packed)` | ✓ |
| `OS.get_ticks_msec()` | `Time.get_ticks_msec()` | ✓ |
| `OS.window_size`, `OS.window_fullscreen` | `get_window().size`, `DisplayServer.window_set_mode(...)` | ✓ |
| `BUTTON_LEFT` | `MOUSE_BUTTON_LEFT` | ✓ |
| `Engine.editor_hint` | `Engine.is_editor_hint()` | ✓ |
| `rect_position`, `rect_size`, `rect_min_size` | `position`, `size`, `custom_minimum_size` | ✓ |
| `RayCast2D.cast_to` | `target_position` | ✓ |
| `get_tree().set_input_as_handled()` | `get_viewport().set_input_as_handled()` | ✓ |

## Things the guard can't see

- Signal argument changes (for example `body_entered` handlers that expected extra binds): read the class reference.
- `.tscn` files saved by Godot 3 (`format=2`). Never hand-convert scenes; open the project in the Godot 4 editor
  and let it convert, after a commit.
- Shader changes (`hint_color` → `source_color`, renamed built-ins). Check shaders against the shading reference.

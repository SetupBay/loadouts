#!/usr/bin/env python3
"""Find Godot 3 GDScript and API names in a Godot 4 project.

Usage: python3 gd3_guard.py [PATH ...]        (default: the current folder)
       python3 gd3_guard.py --list            (print every rule)

Scans .gd files (skips .godot/ and addons/ unless named). Prints one line per finding:
  path:line: [rule] what is wrong -> what Godot 4 uses
Exit 0 when nothing at "error" level is found, 1 when something is, 2 on bad usage.
Standard library only. Read-only: it never edits a file.
"""
import os
import re
import sys

# (rule id, level, regex, message). Patterns are matched against code with comments and strings removed.
RULES = [
    ("yield", "error", r"\byield\s*\(", "yield() was removed -> await signal (await get_tree().create_timer(t).timeout)"),
    ("onready-keyword", "error", r"^\s*onready\s+var\b", "onready keyword -> @onready var"),
    ("export-keyword", "error", r"^\s*export\b(\s*\(.*\))?\s+var\b", "export keyword -> @export var (@export_range, @export_enum, ...)"),
    ("tool-keyword", "error", r"^\s*tool\s*$", "tool keyword -> @tool annotation"),
    ("setget", "error", r"\bsetget\b", "setget -> property syntax: var x: int: set = _set_x, get = _get_x"),
    ("rpc-keywords", "error", r"^\s*(remote|remotesync|master|mastersync|puppet|puppetsync)\s+func\b", "network keywords -> @rpc(\"any_peer\") / @rpc(\"authority\") annotations"),
    ("connect-string-target", "error", r"\.connect\(\s*\"[A-Za-z_]\w*\"\s*,\s*[A-Za-z_]\w*\s*,", "connect(\"signal\", obj, \"method\") -> signal_name.connect(obj.method)"),
    ("kinematic-body", "error", r"\bKinematicBody(2D)?\b", "KinematicBody / KinematicBody2D -> CharacterBody3D / CharacterBody2D"),
    ("spatial", "error", r"\b(Spatial|SpatialMaterial)\b", "Spatial -> Node3D, SpatialMaterial -> StandardMaterial3D"),
    ("move-and-slide-args", "error", r"\bmove_and_slide\(\s*[^)\s]", "move_and_slide(velocity, ...) -> set velocity (and up_direction), then move_and_slide()"),
    ("instance", "error", r"\.instance\(\s*\)", "PackedScene.instance() -> instantiate()"),
    ("array-empty", "error", r"\.empty\(\s*\)", ".empty() -> .is_empty()"),
    ("deg2rad", "error", r"\b(deg2rad|rad2deg)\s*\(", "deg2rad / rad2deg -> deg_to_rad / rad_to_deg"),
    ("rand-range", "error", r"\brand_range\s*\(", "rand_range -> randf_range (floats) or randi_range (ints)"),
    ("stepify", "error", r"\bstepify\s*\(", "stepify -> snapped"),
    ("str2var", "error", r"\b(str2var|var2str|bytes2var|var2bytes)\s*\(", "str2var / var2str -> str_to_var / var_to_str"),
    ("linear-interpolate", "error", r"\.linear_interpolate\s*\(", "linear_interpolate -> lerp"),
    ("pool-arrays", "error", r"\bPool(Byte|Int|Real|String|Vector2|Vector3|Color)Array\b", "PoolXArray -> PackedXArray (PoolRealArray -> PackedFloat32Array)"),
    ("change-scene", "error", r"\.change_scene\s*\(", "change_scene(path) -> change_scene_to_file(path)"),
    ("change-scene-to", "error", r"\.change_scene_to\s*\(", "change_scene_to(packed) -> change_scene_to_packed(packed)"),
    ("os-ticks", "error", r"\bOS\.get_(ticks_msec|ticks_usec|unix_time|datetime)\s*\(", "OS time functions -> Time.get_ticks_msec(), Time.get_unix_time_from_system(), ..."),
    ("mouse-button", "error", r"\bBUTTON_(LEFT|RIGHT|MIDDLE|WHEEL_UP|WHEEL_DOWN)\b", "BUTTON_LEFT -> MOUSE_BUTTON_LEFT"),
    ("file-directory", "error", r"\b(File|Directory)\.new\(\s*\)", "File.new() / Directory.new() -> FileAccess.open(...) / DirAccess.open(...)"),
    ("funcref", "error", r"\bfuncref\s*\(", "funcref(obj, \"m\") -> Callable(obj, \"m\") or obj.m"),
    ("tween-node", "error", r"\.interpolate_property\s*\(|\bTween\.new\(\s*\)", "Tween node -> var t := create_tween(); t.tween_property(...)"),
    ("editor-hint", "error", r"\bEngine\.editor_hint\b", "Engine.editor_hint -> Engine.is_editor_hint()"),
    ("rect-props", "error", r"\brect_(position|size|min_size|rotation|scale|global_position|pivot_offset)\b", "Control rect_* -> position, size, custom_minimum_size, rotation, scale, pivot_offset"),
    ("raycast-cast-to", "error", r"\bcast_to\b", "RayCast cast_to -> target_position"),
    ("renamed-nodes", "error", r"\b(Position2D|Position3D|VisibilityNotifier2D|VisibilityNotifier|YSort|Navigation2D|Particles2D|Light2D\.MODE_)\b", "renamed or removed node -> Marker2D/3D, VisibleOnScreenNotifier2D/3D, y_sort_enabled, NavigationAgent2D, GPUParticles2D"),
    ("set-input-handled", "error", r"get_tree\(\)\.set_input_as_handled\s*\(", "get_tree().set_input_as_handled() -> get_viewport().set_input_as_handled()"),
    ("os-window", "error", r"\bOS\.(window_size|window_fullscreen|set_window_title|window_position)\b", "OS window API -> get_window().size / DisplayServer.window_set_mode(...)"),
    ("emit-signal-string", "warn", r"\bemit_signal\(\s*\"", "emit_signal(\"x\") still works, but Godot 4 style is x.emit(...)"),
    ("tilemap-node", "warn", r"\bextends\s+TileMap\b|:\s*TileMap\b", "TileMap is deprecated since Godot 4.3 -> one TileMapLayer node per layer"),
    ("untyped-func", "warn", r"^\s*func\s+\w+\([^)]*\)\s*:", "function without a return type -> add -> void (or the type it returns)"),
]
COMPILED = [(rid, lvl, re.compile(rx), msg) for rid, lvl, rx, msg in RULES]
SKIP_DIRS = {".godot", ".import", ".git", ".agents", ".claude", ".cursor", "addons", "build", "export"}


def code_only(line):
    """Drop string contents and trailing comments, keeping quote marks so patterns can see a string was there."""
    out, i, q = [], 0, None
    while i < len(line):
        c = line[i]
        if q:
            if c == "\\":
                i += 2
                continue
            if c == q:
                q = None
                out.append(c)
            i += 1
            continue
        if c in "\"'":
            q = c
            out.append(c)
        elif c == "#":
            break
        else:
            out.append(c)
        i += 1
    return "".join(out)


def keep_strings_for(rule_id):
    # A few rules need to see that the first argument is a string literal (not its contents).
    return rule_id in ("connect-string-target", "emit-signal-string")


def scan_file(path):
    found = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for n, raw in enumerate(fh, 1):
            stripped = code_only(raw.rstrip("\n"))
            if not stripped.strip():
                continue
            for rid, lvl, rx, msg in COMPILED:
                # Strings are reduced to "" by code_only; patterns that need a quoted first arg match `""`.
                text = stripped
                if keep_strings_for(rid):
                    text = re.sub(r"\"\"", "\"s\"", stripped)
                if rx.search(text):
                    found.append((path, n, rid, lvl, msg))
    return found


def iter_files(paths):
    for p in paths:
        if os.path.isfile(p):
            if p.endswith(".gd"):
                yield p
            continue
        for root, dirs, files in os.walk(p):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for f in sorted(files):
                if f.endswith(".gd"):
                    yield os.path.join(root, f)


def main(argv):
    if argv[:1] == ["--list"]:
        for rid, lvl, _, msg in RULES:
            print(f"{lvl:5} {rid:22} {msg}")
        return 0
    if any(a.startswith("-") for a in argv):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    paths = argv or ["."]
    files = list(iter_files(paths))
    findings = [f for path in files for f in scan_file(path)]
    for path, n, rid, lvl, msg in findings:
        print(f"{os.path.relpath(path)}:{n}: {lvl} [{rid}] {msg}")
    errors = sum(1 for f in findings if f[3] == "error")
    warns = len(findings) - errors
    print(f"gd3-guard: {len(files)} file(s), {errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

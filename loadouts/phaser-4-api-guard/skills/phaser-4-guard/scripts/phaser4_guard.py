#!/usr/bin/env python3
"""Find Phaser 3 APIs that Phaser 4 removed or changed, in a Phaser 4 game's .ts/.js files.

Usage: python3 phaser4_guard.py [PATH ...]        (default: the current folder)
       python3 phaser4_guard.py --list            (print every rule)

A "guard: ok" comment on a line silences its warnings (never its errors).
Prints one line per finding:  path:line: level [rule] what is wrong -> what to use
Exit 0 when nothing at "error" level is found, 1 when something is, 2 on bad usage.
Standard library only. Read-only: it never edits a file and makes no network calls.
"""
import fnmatch
import os
import re
import sys

# (rule id, level, regex, message, file patterns). Patterns run against each line with comments removed.
RULES = [
    ('set-pipeline', 'error', '\\.setPipeline\\(|\\.setPostPipeline\\(|\\.resetPipeline\\(|pipelines\\.(add|get)\\(',
     'pipelines were removed in Phaser 4 -> render nodes (RenderConfig#renderNodes); for lights use setLighting(true)', []),
    ('prefx-postfx', 'error', '\\.(preFX|postFX)\\b',
     'preFX/postFX were replaced by filters -> obj.filters.internal / obj.filters.external (enable with obj.enableFilters())', []),
    ('bitmap-mask', 'error', '\\bBitmapMask\\b|\\.createBitmapMask\\(',
     'BitmapMask was removed -> obj.filters.internal.addMask(maskObject)', []),
    ('geometry-mask-webgl', 'warn', '\\bcreateGeometryMask\\(|\\bGeometryMask\\b',
     'GeometryMask only works in the Canvas renderer in Phaser 4 -> the Mask filter for WebGL', []),
    ('set-tint-fill', 'error', '\\.setTintFill\\(|\\.tintFill\\b',
     'setTintFill()/tintFill were removed -> setTint(c).setTintMode(Phaser.TintModes.FILL)', []),
    ('geom-point', 'error', '\\bGeom\\.Point\\b',
     'Geom.Point was removed -> Phaser.Math.Vector2', []),
    ('math-pi2', 'error', '\\bMath\\.PI2\\b',
     'Phaser.Math.PI2 was removed -> Phaser.Math.TAU (now PI * 2)', []),
    ('struct-set-map', 'error', '\\bStructs\\.(Set|Map)\\b',
     'Phaser.Structs.Set/Map were removed -> native Set / Map', []),
    ('mesh-plane', 'error', '\\.add\\.(mesh|plane)\\(|\\bGameObjects\\.(Mesh|Plane)\\b',
     'Mesh and Plane were removed in Phaser 4', []),
    ('textures-generate', 'error', '\\btextures\\.generate\\(|\\bCreate\\.GenerateTexture\\b',
     'TextureManager.generate / Create.GenerateTexture were removed -> draw to a Graphics and generateTexture(), or load an image', []),
    ('bloom-shine-fx', 'error', '\\.add(Bloom|Shine|Circle|Gradient)\\(',
     'the Bloom/Shine/Circle/Gradient FX were removed -> Phaser.Actions.AddEffectBloom/AddEffectShine/AddMaskShape, or the Gradient game object', []),
    ('color-matrix-direct', 'error', '(?<![.\\w])(cm|colorMatrix|matrixFX|cmFX|grade|fx)\\.(sepia|grayscale|blackWhite|brown|vintagePinhole|kodachrome|technicolor|polaroid|shiftToBGR|desaturate|saturate|hue|brightness|contrast|night|lsd|negative)\\(',
     'ColorMatrix methods moved onto .colorMatrix -> filter.colorMatrix.sepia()', []),
    ('spine-bundled', 'error', 'SpinePlugin|phaser/plugins/spine',
     'the bundled Spine plugins are no longer updated -> the official Spine plugin from Esoteric Software', []),
    ('camera3d', 'error', 'Camera3D|Layer3D|phaser-ie9',
     'Camera3D/Layer3D plugins and phaser-ie9 were removed', []),
    ('math-tau', 'warn', '\\bMath\\.TAU\\b',
     'Phaser.Math.TAU is now PI * 2 (in Phaser 3 it was PI / 2) -> check intent; use Math.PI_OVER_2 for a quarter turn', []),
    ('render-texture-draw', 'warn', '\\b(rt|dt|\\w*Texture|\\w*RT)\\.(draw|drawFrame|stamp|erase|fill|repeat)\\(',
     'DynamicTexture/RenderTexture commands are buffered in Phaser 4 -> call .render() after drawing (mark the line guard: ok once it does)', []),
    ('round-pixels', 'warn', '\\broundPixels\\b',
     'roundPixels now defaults to false and only applies to unscaled, axis-aligned objects -> see GameObject#vertexRoundMode', []),
    ('grid-outline', 'warn', '\\b(outlineFillColor|outlineFillAlpha|setOutlineStyle)\\b',
     'Grid shape outline* properties were renamed to stroke* in Phaser 4', []),
    ('raw-gl', 'warn', '\\b(renderer\\.gl|getContext\\(\\s*[\\"\']webgl)',
     "direct WebGL calls desync Phaser 4's WebGL state -> use an Extern game object", []),
    ('phaser3-pin', 'error', '[\\"\']phaser[\\"\']\\s*:\\s*[\\"\'][~^]?3\\.',
     'package.json pins Phaser 3 -> phaser 4.x', ['package.json']),
]
FILES = ['*.ts', '*.tsx', '*.js', '*.mjs', '*.jsx', 'package.json']
COMMENT = '//'
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".agents", ".claude", ".cursor", "dist", "build", "target", ".godot"}
COMPILED = [(rid, lvl, re.compile(rx), msg, globs) for rid, lvl, rx, msg, globs in RULES]


def strip_comment(line):
    """Drop a trailing comment, leaving string literals alone."""
    q = None
    i = 0
    while i < len(line):
        c = line[i]
        if q:
            if c == "\\":
                i += 2
                continue
            if c == q:
                q = None
        elif c in "\"'`":
            q = c
        elif line.startswith(COMMENT, i):
            return line[:i]
        i += 1
    return line


def wanted(name):
    return any(fnmatch.fnmatch(name, g) for g in FILES)


def walk(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
            continue
        for root, dirs, files in os.walk(p):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for f in sorted(files):
                if wanted(f):
                    yield os.path.join(root, f)


def scan(path):
    out = []
    name = os.path.basename(path)
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError as e:
        return [(path, 0, "error", "unreadable", str(e))]
    for n, raw in enumerate(lines, 1):
        code = strip_comment(raw)
        if not code.strip():
            continue
        accepted = "guard: ok" in raw  # a person accepted the warnings on this line
        for rid, lvl, rx, msg, globs in COMPILED:
            if accepted and lvl == "warn":
                continue
            if globs and not any(fnmatch.fnmatch(name, g) for g in globs):
                continue
            if rx.search(code):
                out.append((path, n, lvl, rid, msg))
    return out


def main(argv):
    if "--list" in argv:
        for rid, lvl, _, msg, globs in RULES:
            print(f"{lvl:5} [{rid}] {msg}" + (f"  (only {', '.join(globs)})" if globs else ""))
        return 0
    if any(a.startswith("-") for a in argv):
        print(__doc__)
        return 2
    paths = argv or ["."]
    for p in paths:
        if not os.path.exists(p):
            print(f"no such path: {p}", file=sys.stderr)
            return 2
    files = list(walk(paths))
    findings = []
    for f in files:
        findings.extend(scan(f))
    for path, n, lvl, rid, msg in findings:
        print(f"{os.path.relpath(path)}:{n}: {lvl} [{rid}] {msg}")
    errors = sum(1 for x in findings if x[2] == "error")
    warns = sum(1 for x in findings if x[2] == "warn")
    print(f"phaser4_guard: {len(files)} file(s), {errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

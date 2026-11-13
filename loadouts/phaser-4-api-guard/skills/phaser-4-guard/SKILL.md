---
name: phaser-4-guard
description: Check a Phaser 4 game for Phaser 3 APIs (pipelines, preFX/postFX, BitmapMask, setTintFill, Geom.Point, Math.PI2) and silent changes such as Math.TAU and buffered RenderTexture drawing, then type-check against Phaser 4's own types. Use after writing or editing Phaser scenes, when tsc says a Phaser property doesn't exist, or when porting a Phaser 3 tutorial.
---

# Phaser 4 guard

`npm i phaser` gives you Phaser 4, but most Phaser examples online are Phaser 3. Phaser 4 replaced the renderer,
so the commonest Phaser 3 calls (`setPipeline`, `preFX`, `postFX`, `BitmapMask`) no longer exist. Some changes don't
fail at all: `Math.TAU` changed value, and RenderTexture drawing does nothing until `render()`.

## 1. Confirm the version
- `node -p "require('phaser/package.json').version"` should print `4.x`. If it's `3.x`, stop: this skill is for Phaser 4.

## 2. Scan
```bash
python3 .agents/skills/phaser-4-guard/scripts/phaser4_guard.py src package.json
```
(Use the path the skill was installed to: `.claude/skills/...` for Claude Code, `.agents/skills/...` for the others.)

- Each `error` line is a Phaser 3 API that Phaser 4 removed. Fix it with the replacement on the line, or look it up
  in `references/v3-to-v4.md`.
- Each `warn` line is a change that compiles but may behave differently: `Math.TAU`, a texture `draw()` that may need
  `.render()`, `roundPixels`, `GeometryMask` (Canvas only), Grid `outline*` names, raw WebGL. Check each one. When it's
  right, add `// guard: ok <reason>` to the line.

## 3. Type-check against Phaser 4
```bash
npx tsc --noEmit
```
- Phaser 4's types are generated from its source, so `Property 'postFX' does not exist` means the API is gone, not
  that the types are wrong. Never cast to `any` or add `@ts-ignore` to keep a Phaser 3 call.
- For JavaScript projects, add `// @ts-check` to the file or `"checkJs": true` to get the same errors.

## 4. Read the official guide when porting
Phaser ships agent skills in the package. For anything not in the table, read
`node_modules/phaser/skills/v3-to-v4-migration/SKILL.md`, then the topic skill such as
`node_modules/phaser/skills/filters-and-postfx/SKILL.md`.

## 5. Report
Say which Phaser 3 calls you replaced, which warnings you kept and why, and that the scanner and `tsc` were clean.
If you changed rendering, filters or lighting, say whether you ran the game and looked at it.

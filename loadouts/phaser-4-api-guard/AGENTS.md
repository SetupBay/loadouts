# AGENTS.md: Phaser 4 game (Phaser 3 API guard)

This game runs **Phaser 4** (`phaser` 4.2.x), with TypeScript. `npm i phaser` has installed Phaser 4 since
April 2026, and 3.90.0 was the last Phaser 3 release. Nearly every Phaser tutorial and answer you learnt from is
Phaser 3, and Phaser 4 replaced the renderer: pipelines, preFX/postFX and BitmapMask are gone.

## Check the version first
- Read `package.json`. If `phaser` is `3.x`, this file doesn't apply: write Phaser 3 code and don't use any
  Phaser 4 API. If it's `4.x`, follow the rules below. If you're not sure, stop and ask.
- Phaser 4 ships its own agent skills in the package: `node_modules/phaser/skills/`. Read
  `node_modules/phaser/skills/v3-to-v4-migration/SKILL.md` before porting Phaser 3 code, and the topic skill
  (for example `filters-and-postfx`, `render-textures`) before using an API you're unsure of.
- The types are the truth: `node_modules/phaser/types/phaser.d.ts`. If `tsc` says a property doesn't exist, it's
  gone. Don't cast to `any` to get round it.

## Rules
- Write Phaser 4 code only. The `phaser-4-guard` skill has the table. The common ones are:
  - `setPipeline('Light2D')` → `setLighting(true)` (and `this.lights.enable()`)
  - `preFX` / `postFX` → `obj.enableFilters()`, then `obj.filters.internal` / `obj.filters.external`, or `camera.filters`
  - `BitmapMask` → `obj.filters.internal.addMask(maskObject)`
  - `setTintFill(c)` → `setTint(c).setTintMode(Phaser.TintModes.FILL)`
  - `Geom.Point` → `Phaser.Math.Vector2`. `Structs.Set` / `Map` → native `Set` / `Map`
  - `Math.PI2` → `Math.TAU`. **`Math.TAU` is now `PI * 2`**; in Phaser 3 it was `PI / 2`. Use `Math.PI_OVER_2` for a quarter turn.
  - `colorMatrix.sepia()` → `colorMatrix.colorMatrix.sepia()`
- `RenderTexture` / `DynamicTexture` drawing is buffered: call `.render()` after `draw()`, `stamp()` and so on.
- `roundPixels` now defaults to `false`. For pixel art set `pixelArt: true` or choose a `vertexRoundMode`.
- Don't make raw WebGL calls. Use an `Extern` game object if you need to.
- Don't upgrade or downgrade Phaser without asking.

## Before you say "done"
1. Run the `phaser-4-guard` scanner on `src` and `package.json`. It must report `0 error(s)`. Any warning you leave needs a reason.
2. Run `npx tsc --noEmit`. It must pass, with no new `any` or `@ts-ignore` around Phaser calls.
3. If you changed rendering, filters or lighting, run the game and look at it.

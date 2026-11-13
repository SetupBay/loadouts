# Phaser 3 to Phaser 4, the calls agents get wrong

From the official migration guide shipped in `phaser` 4.2.1 (`node_modules/phaser/changelog/v4/4.0/MIGRATION-GUIDE.md`,
also in the package's v3-to-v4-migration skill). The replacements used in the verifier's Phaser 4 scene type-check against Phaser 4.2.1.

| Phaser 3 | Phaser 4 |
|---|---|
| `sprite.setPipeline("Light2D")` | `sprite.setLighting(true)`; `this.lights.enable()` |
| custom `WebGLPipeline` / `PostFXPipeline` | a render node registered with `RenderConfig#renderNodes` |
| `sprite.preFX.addGlow()` / `sprite.postFX.addBlur()` | `sprite.enableFilters()`; `sprite.filters.internal.addGlow()` / `sprite.filters.external.addBlur()` |
| `camera.postFX.addColorMatrix()` | `camera.filters.external.addColorMatrix()` |
| `cm.sepia()` | `cm.colorMatrix.sepia()` |
| `postFX.addBloom()` / `addShine()` / `addCircle()` | `Phaser.Actions.AddEffectBloom(obj)` / `AddEffectShine(obj)` / `AddMaskShape(obj)` |
| `addGradient()` FX | the `Gradient` game object |
| `new Display.Masks.BitmapMask(scene, obj)` + `setMask` | `sprite.filters.internal.addMask(obj)` |
| `GeometryMask` in WebGL | the `Mask` filter (GeometryMask is Canvas only) |
| `sprite.setTintFill(c)`, `tintFill` | `sprite.setTint(c).setTintMode(Phaser.TintModes.FILL)` |
| `new Geom.Point(x, y)` | `new Phaser.Math.Vector2(x, y)` |
| `Point.GetMagnitude(p)` | `v.length()` |
| `Phaser.Math.PI2` | `Phaser.Math.TAU` |
| `Phaser.Math.TAU` (was PI / 2) | `Phaser.Math.PI_OVER_2` (TAU is now PI * 2) |
| `Phaser.Structs.Set` / `Map` | native `Set` / `Map` |
| `rt.draw(obj)` drawing at once | `rt.draw(obj).render()` (commands are buffered) |
| `this.add.mesh()`, `this.add.plane()` | removed |
| `this.textures.generate(key, { data })` | draw to a `Graphics` and call `generateTexture(key, w, h)` |
| bundled `SpinePlugin` | the official Spine plugin from Esoteric Software |
| `roundPixels` true by default | false by default; `pixelArt: true` or `GameObject#vertexRoundMode` |
| Grid `outlineFillColor`, `setOutlineStyle` | the `stroke*` equivalents |

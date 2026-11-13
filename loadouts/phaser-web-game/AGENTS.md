# AGENTS.md: Phaser 4 web game

Browser game with Phaser 4, TypeScript and Vite. Check the Phaser version in `package.json`; v3 code and tutorials
often do not work in v4.

## Commands
- Dev server: `npm run dev`. Production build: `npm run build`. Type-check: `npx tsc --noEmit`.
- Done means: type-check and build pass, and you ran the game and played the changed part.

## Phaser docs that match the installed version
- Phaser ships agent skills inside the package: `node_modules/phaser/skills/<topic>/SKILL.md` (scenes, loading-assets,
  physics-arcade, input-keyboard-mouse-touch, tweens, filters-and-postfx, v3-to-v4-migration and more).
  Read the relevant one before using an API you have not used in this project. Prefer it over memory and old tutorials.
- Porting v3 code or a v3 example: read `node_modules/phaser/skills/v3-to-v4-migration/SKILL.md` first. FX and masks
  are filters in v4, pipelines are render nodes, and the tint API changed.

## Game code rules
- One scene per screen or mode (Boot, Preload, Menu, Game, GameOver). Scenes talk through events or the registry,
  not by reaching into each other's fields.
- Load assets in `preload()` with stable keys; files live in `public/assets/`. Never load in `update()`.
- Movement and timers use `delta` or Phaser timers, never frame counts, so speed does not depend on frame rate.
- Reuse objects: physics groups with `maxSize` and `get()` / `disableBody` for bullets, particles and enemies.
  No `new` or `destroy` per frame.
- Keep `update()` cheap: no allocations, DOM access or `console.log` in hot paths.
- Game constants (speeds, sizes, timings) in one config module so tuning does not mean hunting through scenes.
- Input: support keyboard and pointer or touch for anything the player must do. Guard `this.input.keyboard` (it can be
  null when disabled).
- Clean up: remove listeners and timers in the scene's `shutdown` event.

## Scope
- Protect the core loop first. New features only after it plays well; one feature per change, playable after each.
- Use the `phaser-feature` skill for every gameplay change.

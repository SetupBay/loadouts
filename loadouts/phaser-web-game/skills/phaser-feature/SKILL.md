---
name: phaser-feature
description: Add a gameplay feature to a Phaser 4 game using the version-matched Phaser skills in node_modules, pooled objects, delta-based movement, and a type-check, build and play test. Use for any gameplay change.
---

# Phaser feature

1. Name the feature in one sentence and the scene it lives in. If it needs a new scene, say so.
2. Read the matching Phaser skill from `node_modules/phaser/skills/` for every subsystem it touches (for example
   `physics-arcade`, `groups-and-containers`, `tweens`). Use the API as written there for the installed version.
3. Implement it like `references/GameScene.ts`: assets in `preload()`, pooled groups, delta-based movement, constants in
   one place, listeners removed on shutdown.
4. Run `npx tsc --noEmit` and `npm run build`.
5. Run `npm run dev`, open the game and play the feature. If you can drive a browser (Playwright MCP or similar), take a
   screenshot of it working; otherwise tell the human exactly what to try.
6. Check the frame rate did not drop (the Phaser debug or browser performance panel) if you added many objects.
7. Report: what changed, how you tested it, any tuning values worth adjusting.

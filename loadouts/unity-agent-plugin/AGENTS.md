# AGENTS.md: Unity 6 with the official Unity agent plugin

This project uses Unity 6+ and Unity's official agent plugin (skills that edit scripts, scenes and assets, and can run
C# in the open Editor through the Unity CLI). Those changes are powerful and not always undoable from the Editor.

## Before changing anything
- `git status` must be clean. If it is not, ask the human to commit or stash first. Commit before every larger change
  (new system, scene restructuring, import-setting changes, package changes).
- Confirm the Unity version (`ProjectSettings/ProjectVersion.txt`) is 6000.x. The plugin requires Unity 6 or later.

## How to change things
- Prefer the plugin's skills and the Editor (through the Unity CLI) for scenes, prefabs, ScriptableObjects and import
  settings. Do not hand-edit `.unity`, `.prefab` or `.asset` YAML unless the human asks; references break silently.
- Every asset has a `.meta` file with its GUID. Move and rename assets in the Editor, or move the `.meta` with the asset.
  Never delete or regenerate `.meta` files.
- Never edit `Library/`, `Temp/`, `Logs/`, `obj/` or `UserSettings/`. They are generated and git-ignored.
- Packages: change `Packages/manifest.json` only when asked, one package per commit, and note the version.
- Scripts: one public type per file, file name matches the class. Use the existing assembly definitions (`.asmdef`).

## Checking your work
- After script changes, check the Editor console for compile errors before anything else.
- Run tests when the project has them:
  `Unity -batchmode -projectPath . -runTests -testPlatform EditMode -testResults ./TestResults/editmode.xml`
  (close the Editor first, or use the Test Runner inside it). PlayMode tests use `-testPlatform PlayMode`.
- For visual changes, ask the human to look, or capture a Game view screenshot through the plugin when available.
- Summarise which scenes, prefabs and assets you changed so the human can review them in the Editor.

Use the `unity-plugin-setup` skill if the plugin is not installed.

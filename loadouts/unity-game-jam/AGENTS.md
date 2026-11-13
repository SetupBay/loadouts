# AGENTS.md: Unity C# game jam

This is a Unity project for a game jam. A finished small game beats an unfinished big one.

## Jam rules
1. Core loop first: start → play → win/lose → restart. Nothing else until that works.
2. Offer the smallest version of any big request and park the rest in `CUTLIST.md`.
3. After the human calls feature freeze: bugs, juice, menus, audio and the build only.
4. Make a web build on day one (see the `unity-web-build` skill) so the final one is routine.

## The editor is part of the codebase
- You cannot see scenes, prefabs or inspector values. When a change needs editor work, say exactly what to do:
  "Select the Player prefab, add a `Health` component, set Max HP to 3".
- **Every asset has a `.meta` file holding its GUID.** When moving or renaming an asset outside Unity, move or rename
  its `.meta` with it, or references across the project break. Never delete `.meta` files. Prefer asking the human to
  rename in the Project window.
- Commit `Assets/`, `Packages/`, `ProjectSettings/`. Ignore `Library/`, `Temp/`, `Obj/`, `Logs/`, `UserSettings/`, `Build*/`.
- Renaming a serialised field loses its inspector value. Use `[FormerlySerializedAs("oldName")]` when renaming.

## C# conventions
- One `MonoBehaviour` per file; file name equals class name.
- Inspector fields: `[SerializeField] private float moveSpeed = 5f;` not public fields. Use `[Header]`, `[Range]`, `[Tooltip]`.
- Cache components in `Awake` (`rb = GetComponent<Rigidbody2D>();`). Use `[RequireComponent]` where a dependency is mandatory.
- Never call `GameObject.Find`, `FindObjectOfType`/`FindFirstObjectByType` or `GetComponent` inside `Update`.
- Physics in `FixedUpdate`; input and visuals in `Update`. Multiply by `Time.deltaTime` (or `fixedDeltaTime`) for frame-rate independence.
- Use `ScriptableObject` assets for tuning data (enemy stats, level settings) so designers tweak without code.
- Events: C# `event Action<int>` or `UnityEvent` for "something happened"; keep singletons to a GameManager and an AudioManager at most.
- Avoid per-frame allocations (LINQ, string concatenation, `new` lists in `Update`) — they cause stutters, especially on web.
- Object-pool anything spawned often (bullets, particles).
- Check which input system the project uses (`Packages/manifest.json` contains `com.unity.inputsystem`?) and stick to it.

## Before you say "done"
- Code compiles: ask the human to check the Console for errors, or run a batch-mode build.
- List the editor steps the human must do, numbered.

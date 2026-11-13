# AGENTS.md: Roblox game with pure Luau modules checked outside Studio

Game rules (prices, inventory, damage, cooldown maths, matchmaking) live in **pure modules** in `src/shared/pure/`.
A pure module never touches the DataModel, so the plain `luau` CLI can type-check and test it in seconds, with no
Studio open. Scripts in `src/server/` and `src/client/` are the **edge**: they get services, read and write
Instances, handle remotes, then call the pure modules with plain values.

## Layout (Rojo)
```
src/shared/pure/   → ReplicatedStorage.Shared.pure   pure ModuleScripts, --!strict, no Roblox APIs
src/shared/        → ReplicatedStorage.Shared        other shared modules and Remotes
src/server/        → ServerScriptService.Server      server edge scripts (*.server.luau)
src/client/        → StarterPlayerScripts            client edge scripts (*.client.luau)
tests/             (not synced)                      *.spec.luau and run.luau, for the luau CLI
```

## Rules for pure modules
- First line `--!strict`. Export the types callers need (`export type State = {...}`).
- No `game`, `workspace`, `script`, `Instance`, services, `task.*`, `wait`/`spawn`/`delay`, `tick()`, or Roblox
  datatypes (`Vector3`, `CFrame`, `Color3`, `Enum`, `Random`). Take what you need as parameters.
- Require other pure modules by string: `require("./Money")`. Roblox (require-by-string) and the luau CLI both
  resolve it relative to the file. Never `require(script.Parent.Money)` inside `pure/`.
- No `print`/`warn`, no `math.random` or `os.time` inside rules. Return values and errors, and take an rng or the
  current time as a parameter, so tests are repeatable.
- Validate inputs in the pure function too (whole numbers, ranges, NaN). The edge script checks types from remotes;
  the rules decide what's allowed.

## Rules for edge scripts
- Keep them thin: read Instances and remote arguments, call the pure module, apply the result.
- Use `task.wait` / `task.spawn` / `task.delay`, never the deprecated `wait` / `spawn` / `delay`.
- The server decides: remotes carry intent, and the server runs the pure rules before changing any state.

## Before you say "done"
1. `python3 .agents/skills/luau-pure-tests/scripts/pure_luau_guard.py src/shared/pure` reports `0 error(s)`.
2. `luau-analyze --mode=strict src/shared/pure tests` reports nothing.
3. `luau tests/run.luau` ends with `0 failed`. Add a test for every rule you change.
4. List what the human should play-test in Studio for the edge scripts. If Roblox Studio's built-in MCP server is
   connected, you can run that play-test through it, but the pure tests above still come first.

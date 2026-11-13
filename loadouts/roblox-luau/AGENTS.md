# AGENTS.md: Roblox Luau (Rojo)

## Layout (Rojo, see `default.project.json`)
```
src/server/   → ServerScriptService     server Scripts (*.server.luau) and server-only modules
src/client/   → StarterPlayerScripts    LocalScripts (*.client.luau)
src/shared/   → ReplicatedStorage       ModuleScripts used by both sides, plus Remotes
```
- `ServerStorage` and `ServerScriptService` are invisible to clients. Anything in `ReplicatedStorage` or the workspace is visible to exploiters.
- Run `rojo serve` and connect from the Studio plugin to sync. Do not edit synced scripts inside Studio — edits are overwritten.

## The golden rule: the server decides
- Clients can be fully controlled by exploiters. Every value from a `RemoteEvent`/`RemoteFunction` is an untrusted request.
- Remotes express intent ("I want to buy item X", "I pressed attack"), never outcomes ("give me 500 coins", "deal 999 damage").
- On the server, for every remote handler:
  1. Check argument types (`typeof(x) == "string"`) and ranges; reject NaN and huge numbers.
  2. Check the player is allowed (owns the item, has the cash, is close enough, cooldown passed).
  3. Rate-limit per player.
  4. Compute the result on the server.
- Never use `RemoteFunction:InvokeClient` — a client can yield forever and hang the server thread.
- Currency, inventory, damage, cooldowns and leaderboards live on the server.

## Luau style
- `--!strict` at the top of every file; type function signatures and module tables.
- `task.wait`, `task.spawn`, `task.delay`, `task.defer` — never the deprecated `wait`, `spawn`, `delay`.
- Get services once at the top: `local Players = game:GetService("Players")`.
- Use `WaitForChild` on the client for replicated objects; avoid it on the server for things the server creates.
- Disconnect connections you create per player or per round, or clean up with a maid/trove pattern.
- `PascalCase` for modules and services, `camelCase` for locals and functions.

## Data
- `DataStoreService` calls can fail: always wrap them in `pcall` and retry with backoff.
- Prefer `UpdateAsync` to `SetAsync` for player data so concurrent servers do not overwrite each other.
- Load on `PlayerAdded`, save on `PlayerRemoving` **and** in `game:BindToClose` (with a time budget), plus periodic autosave.
- Do not save if the initial load failed — you would overwrite real data with defaults.
- Studio needs "Enable Studio Access to API Services" switched on to test DataStores; remind the human.

## Before you say "done"
Code type-checks (`luau-lsp` or Studio's Script Analysis shows no errors), and you have listed what the human should test in a
Studio play-test — ideally with two players (Test → Clients and Servers).

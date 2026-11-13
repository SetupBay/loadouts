---
name: luau-pure-tests
description: Keep a Roblox game's rules in pure Luau modules and run their tests outside Studio with the luau CLI, checking purity with a scanner and types with luau-analyze in strict mode. Use when writing or changing game logic (prices, inventory, damage, cooldowns), when asked to add tests to a Roblox project, or when a module can't run in a test because it calls Roblox APIs.
---

# Pure Luau modules, checked outside Studio

Roblox logic is usually tried out by pressing Play. Rules that don't touch the DataModel can be checked by the
standalone Luau tools instead: `luau-analyze` type-checks them, and `luau` runs their tests in milliseconds.
That's something an agent can run after every change.

## Tools
The Luau release (https://github.com/luau-lang/luau/releases) ships `luau` (runs scripts) and
`luau-analyze` (type-checks and lints) for Linux, macOS and Windows. Rokit or Aftman can install them per project;
otherwise download the release zip. Check with `luau-analyze --help`.

## 1. Check purity
```bash
python3 .agents/skills/luau-pure-tests/scripts/pure_luau_guard.py src/shared/pure
```
(Use the path the skill was installed to: `.claude/skills/...` for Claude Code, `.agents/skills/...` for the others.)

Run it on the pure folders only; edge scripts are meant to use Roblox APIs. Each `error` is a Roblox-only call that
stops the module running outside Studio. Move that call into the edge script and pass the value in. `warn` lines
(`math.random`, `os.time`, `print`) make tests unrepeatable; take an rng or the time as a parameter.

## 2. Type-check in strict mode
```bash
luau-analyze --mode=strict src/shared/pure tests
```
It must print nothing. `Unknown global 'game'` or `Unknown require: unsupported path` means a Roblox API or an
Instance-path require got into a pure module.

## 3. Run the tests
Copy `references/run.luau` to `tests/run.luau` once and list each spec file in it. A spec returns a list of cases:
```luau
--!strict
local Inventory = require("../src/shared/pure/Inventory")
return {
	{ name = "Inventory: the stack limit holds", run = function()
		local s = Inventory.new(500)
		assert(Inventory.buy(s, { id = "sword", price = 150, stack = 1 }, 1))
		assert(not Inventory.buy(s, { id = "sword", price = 150, stack = 1 }, 1))
	end },
}
```
```bash
luau tests/run.luau
```
It prints `PASS`/`FAIL` per case and `N passed, M failed`, and exits non-zero on any failure.

## 4. Report
Say which rules changed, which tests you added, and that the scanner, `luau-analyze --mode=strict` and
`luau tests/run.luau` were clean. Then list what still needs a Studio play-test: the edge scripts, remotes and
anything that touches Instances.

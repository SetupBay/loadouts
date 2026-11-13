--!strict
-- Minimal test runner for the luau CLI: luau tests/run.luau
local specs = { require("./Inventory.spec"), require("./Money.spec") }

local passed, failed = 0, 0
for _, spec in specs do
	for _, case in spec do
		local ok, err = pcall(case.run)
		if ok then
			passed += 1
			print(`PASS {case.name}`)
		else
			failed += 1
			print(`FAIL {case.name}: {err}`)
		end
	end
end
print(`{passed} passed, {failed} failed`)
if failed > 0 then
	error(`{failed} test(s) failed`, 0)
end

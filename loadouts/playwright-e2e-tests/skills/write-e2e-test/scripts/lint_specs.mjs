#!/usr/bin/env node
// Flags Playwright test anti-patterns: fixed waits, non-retrying assertions, brittle selectors, force clicks, test.only.
// Usage: node lint_specs.mjs <dir-or-file> [...]. Exit 1 on any finding. Reads files only.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const RULES = [
  [/\bwaitForTimeout\s*\(/, "fixed wait: wait for a locator or assertion instead"],
  [/waitForLoadState\(\s*["']networkidle["']/, "networkidle is discouraged: wait for the element you need"],
  [/expect\(\s*await\s+.*\.(?:isVisible|isHidden|isChecked|isEnabled|textContent|innerText|count)\(\)\s*\)/, "non-retrying assertion: use a web-first assertion such as toBeVisible() or toHaveText()"],
  [/\bforce\s*:\s*true/, "force: true hides real problems: fix the locator or the app"],
  [/\btest\.only\(|\bdescribe\.only\(/, "test.only must not be committed"],
  [/\bpage\.\$\$?\(|\bpage\.\$eval\(/, "page.$ is the old API: use page.locator or getByRole"],
  [/locator\(\s*["'`][^"'`]*(?::nth-child|:nth-of-type|\/\/|>>|\.[a-z][\w-]*\s+\.[a-z])/i, "brittle selector: prefer getByRole, getByLabel or getByTestId"],
  [/\bsetTimeout\s*\(/, "setTimeout in a test: wait for state instead"],
  [/\.toBeTruthy\(\)/, "toBeTruthy proves little: assert the actual value or state"],
];

function files(p, out = []) {
  if (statSync(p).isDirectory()) {
    for (const n of readdirSync(p)) if (n !== "node_modules") files(join(p, n), out);
  } else if (/\.(?:spec|test)\.[cm]?[jt]sx?$/.test(p)) out.push(p);
  return out;
}

const targets = process.argv.slice(2);
if (!targets.length) {
  console.error("usage: node lint_specs.mjs <dir-or-file> [...]");
  process.exit(2);
}
const findings = [];
const all = targets.flatMap((t) => files(t));
for (const f of all) {
  readFileSync(f, "utf8").split("\n").forEach((line, i) => {
    for (const [re, msg] of RULES) if (re.test(line)) findings.push(`${f}:${i + 1}: ${msg}`);
  });
}
for (const x of findings) console.log(x);
console.log(findings.length ? `${findings.length} finding(s) in ${all.length} file(s)` : `ok: ${all.length} spec file(s), no findings`);
process.exit(findings.length ? 1 : 0);

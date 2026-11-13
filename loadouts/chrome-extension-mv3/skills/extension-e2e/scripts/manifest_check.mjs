#!/usr/bin/env node
// Check a built MV3 extension against the loadout's rules. Node standard library only.
//   node manifest_check.mjs [dist dir] [PERMISSIONS.md]
// Fails on: MV2 keys, a missing service worker or popup file, risky permissions, permissions with no line in
// PERMISSIONS.md, a CSP that allows remote code or eval, eval/new Function or remote scripts in the package.
import fs from "node:fs";
import path from "node:path";

const dist = path.resolve(process.argv[2] ?? "dist");
const permsDoc = process.argv[3] ?? "PERMISSIONS.md";
const problems = [];
const exists = (p) => fs.existsSync(path.join(dist, p));
if (!exists("manifest.json")) {
  console.error(`✗ no manifest.json in ${dist}; build first`);
  process.exit(1);
}
const m = JSON.parse(fs.readFileSync(path.join(dist, "manifest.json"), "utf8"));
if (m.manifest_version !== 3) problems.push("manifest_version must be 3");
if (!/^\d+(\.\d+){0,3}$/.test(m.version ?? "")) problems.push("version must be 1-4 dot-separated integers");
if (!m.name || m.name.length > 75) problems.push("name is required (max 75 characters)");
if (!m.description || m.description.length > 132) problems.push("description is required (max 132 characters)");
if (m.browser_action || m.page_action) problems.push("use action, not browser_action or page_action");
const bg = m.background ?? {};
if (bg.scripts || bg.page || "persistent" in bg) problems.push("background must be a service_worker (no page, scripts or persistent)");
if (bg.service_worker && !exists(bg.service_worker)) problems.push(`service worker ${bg.service_worker} is not in the package`);
if (bg.type && bg.type !== "module") problems.push("background.type must be module if set");
if (m.action?.default_popup && !exists(m.action.default_popup)) problems.push(`popup ${m.action.default_popup} is not in the package`);
const perms = [...(m.permissions ?? []), ...(m.host_permissions ?? [])];
for (const p of ["<all_urls>", "*://*/*", "tabs", "history", "cookies", "webRequest", "webRequestBlocking", "debugger"])
  if (perms.includes(p)) problems.push(`avoid "${p}" (least privilege; use activeTab or optional_host_permissions)`);
const justified = fs.existsSync(permsDoc) ? fs.readFileSync(permsDoc, "utf8") : "";
if (!justified && perms.length) problems.push(`${permsDoc} is missing; every permission needs a one-line reason`);
else for (const p of perms) if (!justified.includes(`\`${p}\``)) problems.push(`permission ${p} has no line in ${permsDoc}`);
const csp = JSON.stringify(m.content_security_policy ?? "");
if (/https?:/.test(csp) || /unsafe-eval/.test(csp)) problems.push("CSP must not allow remote code or eval");
const files = fs.readdirSync(dist, { recursive: true }).map(String).filter((f) => fs.statSync(path.join(dist, f)).isFile());
for (const f of files.filter((f) => /\.(m?js|html)$/.test(f))) {
  const text = fs.readFileSync(path.join(dist, f), "utf8");
  if (/\beval\(|new Function\(/.test(text)) problems.push(`${f}: eval or new Function (dynamic code)`);
  if (/<script[^>]+src=["']https?:/i.test(text) || /import\s*\(?\s*["']https?:/.test(text)) problems.push(`${f}: loads remote code`);
  if (f.endsWith(".html"))
    for (const [, src] of text.matchAll(/<script[^>]+src="([^"]+)"/g))
      if (!/^https?:/.test(src) && !exists(path.join(path.dirname(f), src))) problems.push(`${f}: script ${src} is not in the package`);
}
if (problems.length) {
  for (const p of problems) console.error(`✗ ${p}`);
  console.error(`${problems.length} problem(s)`);
  process.exit(1);
}
console.log(`ok: Manifest V3 valid, ${perms.length} permissions all justified, no remote code, every referenced file present`);

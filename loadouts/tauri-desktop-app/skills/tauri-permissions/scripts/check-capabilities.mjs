#!/usr/bin/env node
// Least-privilege check for Tauri 2 capabilities. Usage: node check-capabilities.mjs <src-tauri dir>
// Exit 1 with one line per finding; exit 0 and "ok" when clean. Reads JSON capability files and tauri.conf.json only.
import fs from "node:fs";
import path from "node:path";

const root = process.argv[2] ?? "src-tauri";
const findings = [];
const SENSITIVE = /^(fs|shell|http|process|sql|store|websocket|upload):/;
const NEEDS_SCOPE = /^(fs|http):/;
const SHELL_EXEC = /^shell:(allow-execute|allow-spawn|allow-stdin-write|default)$/;

const readJson = (p) => {
  try { return JSON.parse(fs.readFileSync(p, "utf8")); } catch (e) { findings.push(`${p}: not valid JSON (${e.message})`); return null; }
};

const conf = readJson(path.join(root, "tauri.conf.json"));
const inline = conf?.app?.security?.capabilities?.filter((c) => typeof c === "object") ?? [];
if (conf && !conf.app?.security?.csp) findings.push("tauri.conf.json: app.security.csp is missing or null; keep a Content Security Policy");

const capDir = path.join(root, "capabilities");
const files = fs.existsSync(capDir) ? fs.readdirSync(capDir).filter((f) => f.endsWith(".json")) : [];
const caps = [
  ...files.map((f) => ({ where: `capabilities/${f}`, cap: readJson(path.join(capDir, f)) })),
  ...inline.map((c, i) => ({ where: `tauri.conf.json capability #${i + 1}`, cap: c })),
].filter((x) => x.cap);

for (const { where, cap } of caps) {
  const perms = (cap.permissions ?? []).map((p) => (typeof p === "string" ? { identifier: p } : p));
  const wildcard = (cap.windows ?? []).includes("*") || (cap.webviews ?? []).includes("*");
  for (const p of perms) {
    const id = p.identifier ?? "";
    if (wildcard && SENSITIVE.test(id)) findings.push(`${where}: ${id} granted to every window ("*"); name the windows`);
    if (SHELL_EXEC.test(id)) findings.push(`${where}: ${id} lets the frontend run programs; use shell:allow-open or the opener plugin`);
    const scoped = (p.allow ?? []).length > 0;
    const isScopeOnly = /:scope/.test(id);
    if (NEEDS_SCOPE.test(id) && !scoped && !isScopeOnly) findings.push(`${where}: ${id} has no "allow" scope; limit it to the paths or URLs you need`);
  }
  if (cap.remote?.urls?.length && perms.length) findings.push(`${where}: remote URLs ${cap.remote.urls.join(", ")} get ${perms.length} permission(s); needs explicit approval`);
}

if (findings.length) {
  for (const f of findings) console.log(`finding: ${f}`);
  console.log(`${findings.length} finding(s) in ${caps.length} capability set(s)`);
  process.exit(1);
}
console.log(`ok: ${caps.length} capability set(s), least privilege`);

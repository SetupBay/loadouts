#!/usr/bin/env node
// Check a Cloudflare Agents SDK project's wiring before deploy: every exported Agent class has a Durable Object
// binding and SQLite storage (exports or legacy migrations), bindings point at real classes, nodejs_compat and a
// compatibility_date are set, and the TypeScript target suits @callable() decorators.
// Usage: node check_agents_config.mjs [--config wrangler.jsonc] [--src src] [--tsconfig tsconfig.json]
// Read-only; Node standard library only. Exits 1 when something needs fixing.
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const opt = (n, d) => { const i = args.indexOf(`--${n}`); return i >= 0 ? args[i + 1] : d; };
const cfgPath = opt("config", ["wrangler.jsonc", "wrangler.json"].find((f) => fs.existsSync(f)) ?? "wrangler.jsonc");
const srcDir = opt("src", "src");
const tsPath = opt("tsconfig", "tsconfig.json");
let problems = 0;
const fix = (m) => { problems++; console.log(`fix  ${m}`); };
const ok = (m) => console.log(`ok   ${m}`);

// JSONC: drop comments outside strings, then trailing commas.
function parseJsonc(text) {
  let out = "", inStr = false, i = 0;
  while (i < text.length) {
    const c = text[i], n = text[i + 1];
    if (inStr) { out += c; if (c === "\\") { out += n; i += 2; continue; } if (c === '"') inStr = false; i++; continue; }
    if (c === '"') { inStr = true; out += c; i++; continue; }
    if (c === "/" && n === "/") { while (i < text.length && text[i] !== "\n") i++; continue; }
    if (c === "/" && n === "*") { i = text.indexOf("*/", i + 2) + 2; continue; }
    out += c; i++;
  }
  return JSON.parse(out.replace(/,(\s*[}\]])/g, "$1"));
}

if (!fs.existsSync(cfgPath)) { console.log(`fix  no wrangler.jsonc or wrangler.json found (wrangler.toml is not read by this check)`); process.exit(1); }
const cfg = parseJsonc(fs.readFileSync(cfgPath, "utf8"));

// Agent classes exported from source.
const files = [];
(function walk(d) { if (!fs.existsSync(d)) return; for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); if (e.isDirectory()) walk(p); else if (/\.(ts|tsx|js|mjs)$/.test(e.name)) files.push(p); } })(srcDir);
const classes = new Map();
let usesCallable = false;
for (const f of files) {
  const t = fs.readFileSync(f, "utf8");
  for (const m of t.matchAll(/export\s+class\s+(\w+)\s+extends\s+(Agent|AIChatAgent|McpAgent|Think)\b/g)) classes.set(m[1], f);
  if (/@callable\s*\(/.test(t)) usesCallable = true;
}
if (!classes.size) fix(`no exported Agent classes found under ${srcDir}/`);
else ok(`Agent classes: ${[...classes.keys()].join(", ")}`);

if ((cfg.compatibility_flags ?? []).includes("nodejs_compat")) ok("nodejs_compat flag set");
else fix(`${cfgPath}: add "nodejs_compat" to compatibility_flags (the agents package needs it)`);
if (/^\d{4}-\d{2}-\d{2}$/.test(cfg.compatibility_date ?? "")) ok(`compatibility_date ${cfg.compatibility_date}`);
else fix(`${cfgPath}: set compatibility_date (YYYY-MM-DD)`);

const bindings = cfg.durable_objects?.bindings ?? [];
const sqlite = new Set(), kvBacked = new Set();
for (const [name, e] of Object.entries(cfg.exports ?? {})) if (e?.type === "durable-object") (e.storage === "sqlite" ? sqlite : kvBacked).add(name);
for (const m of cfg.migrations ?? []) { for (const c of m.new_sqlite_classes ?? []) sqlite.add(c); for (const c of m.new_classes ?? []) kvBacked.add(c); }
const tags = (cfg.migrations ?? []).map((m) => m.tag);
if (new Set(tags).size !== tags.length) fix(`${cfgPath}: migration tags must be unique (${tags.join(", ")})`);

for (const cls of classes.keys()) {
  const b = bindings.find((x) => x.class_name === cls);
  if (!b) fix(`${cls}: no durable_objects binding with class_name "${cls}"`);
  else if (b.script_name) ok(`${cls}: bound as env.${b.name} (from Worker ${b.script_name})`);
  else ok(`${cls}: bound as env.${b.name}`);
  if (kvBacked.has(cls)) fix(`${cls}: declared with key-value storage; Agents need SQLite ("storage": "sqlite" in exports, or new_sqlite_classes)`);
  else if (!sqlite.has(cls)) fix(`${cls}: no storage declared; add "exports": { "${cls}": { "type": "durable-object", "storage": "sqlite" } }`);
  else ok(`${cls}: SQLite storage declared`);
}
for (const b of bindings) {
  if (!b.script_name && classes.size && !classes.has(b.class_name)) fix(`binding ${b.name} points at class "${b.class_name}", which no source file exports (renamed? Renames and deletions need an explicit exports or migrations change, or stored data is lost)`);
}

if (usesCallable) {
  if (!fs.existsSync(tsPath)) fix(`@callable() is used but ${tsPath} is missing`);
  else {
    const ts = parseJsonc(fs.readFileSync(tsPath, "utf8"));
    const target = String(ts.compilerOptions?.target ?? "").toUpperCase();
    if (ts.extends === "agents/tsconfig") ok(`${tsPath} extends agents/tsconfig`);
    else if (target === "ES2021") ok(`${tsPath}: target ES2021 for @callable()`);
    else fix(`${tsPath}: @callable() needs target ES2021; extend "agents/tsconfig" or set compilerOptions.target to "ES2021"${target ? ` (now ${target})` : ""}`);
    if (ts.compilerOptions?.experimentalDecorators) fix(`${tsPath}: remove experimentalDecorators; @callable() uses standard decorators`);
  }
}

console.log(problems ? `agents-config: ${problems} to fix` : "agents-config: ready");
process.exit(problems ? 1 : 0);

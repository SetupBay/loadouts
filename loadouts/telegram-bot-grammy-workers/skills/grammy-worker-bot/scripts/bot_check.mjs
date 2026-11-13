#!/usr/bin/env node
// Check a grammY-on-Workers project for the mistakes that leak the token or cause retry storms.
// Node standard library only. Usage: node bot_check.mjs [project dir]
import fs from "node:fs";
import path from "node:path";

const dir = path.resolve(process.argv[2] ?? ".");
const out = [];
const add = (level, file, msg) => out.push([level, file, msg]);
const read = (p) => (fs.existsSync(path.join(dir, p)) ? fs.readFileSync(path.join(dir, p), "utf8") : null);
const TOKEN = /\b\d{6,12}:[A-Za-z0-9_-]{30,}\b/;
const SECRET_NAMES = /(TOKEN|SECRET|API_KEY|PASSWORD)/;

// Wrangler config
const cfgName = ["wrangler.jsonc", "wrangler.json", "wrangler.toml"].find((f) => read(f) !== null);
if (!cfgName) add("fix", "wrangler.jsonc", "no Wrangler config found");
else {
  const cfg = read(cfgName);
  if (TOKEN.test(cfg)) add("fix", cfgName, "contains a Telegram bot token; revoke it with @BotFather and use wrangler secret put");
  const varsBlock = cfgName.endsWith(".toml")
    ? (cfg.match(/^\[vars\]([\s\S]*?)(?=^\[|$(?![\s\S]))/m) ?? [])[1] ?? ""
    : (cfg.match(/"vars"\s*:\s*\{([\s\S]*?)\}\s*(,|\n\s*\})/) ?? [])[1] ?? "";
  for (const [, name] of varsBlock.matchAll(/"?([A-Z][A-Z0-9_]*)"?\s*[:=]/g))
    if (SECRET_NAMES.test(name)) add("fix", cfgName, `${name} is in vars, which are plain text in the config and dashboard; make it a secret`);
  if (!/compatibility_date/.test(cfg)) add("warn", cfgName, "no compatibility_date");
}

// Git hygiene
const gi = read(".gitignore") ?? "";
if (!/^\.dev\.vars/m.test(gi)) add("fix", ".gitignore", ".dev.vars is not ignored; local secrets would be committed");

// Source
const walk = (d) => fs.existsSync(d) ? fs.readdirSync(d, { withFileTypes: true }).flatMap((e) => e.name === "node_modules" ? [] : e.isDirectory() ? walk(path.join(d, e.name)) : /\.(m?[jt]s)$/.test(e.name) ? [path.join(d, e.name)] : []) : [];
const files = walk(path.join(dir, "src"));
if (!files.length) add("fix", "src", "no source files");
let hasCatch = false;
for (const f of files) {
  const rel = path.relative(dir, f);
  const raw = fs.readFileSync(f, "utf8");
  const src = raw.replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:"'`])\/\/.*$/gm, "$1"); // drop comments
  if (TOKEN.test(raw)) add("fix", rel, "contains a Telegram bot token; revoke it and read it from env");
  if (/\bbot\.start\(/.test(src)) add("fix", rel, "bot.start() is long polling; a Worker only answers requests, so use webhookCallback");
  for (const m of src.matchAll(/webhookCallback\(([^;]*?)\)\s*(\(|;)/gs))
    if (!/secretToken/.test(m[1])) add("fix", rel, "webhookCallback without secretToken: anyone who finds the URL can send fake updates");
  if (/new Bot\(/.test(src) && !/botInfo/.test(src)) add("warn", rel, "new Bot() without botInfo calls getMe on every cold request; put the getMe JSON in BOT_INFO");
  if (/onTimeout\s*:\s*["']return["']/.test(src)) add("warn", rel, "onTimeout 'return' hides slow handlers; move slow work to a Queue instead");
  if (/\.errorBoundary\(/.test(src)) hasCatch = true;
}
if (files.length && !hasCatch) add("warn", "src", "no errorBoundary(): with webhooks a handler error fails the request and Telegram resends the update (bot.catch only covers long polling)");

for (const [level, file, msg] of out) console.log(`${level.padEnd(4)} ${file}: ${msg}`);
const n = (l) => out.filter((o) => o[0] === l).length;
console.log(`checked ${files.length} source file(s); ${n("fix")} to fix, ${n("warn")} warnings`);
process.exit(n("fix") ? 1 : 0);

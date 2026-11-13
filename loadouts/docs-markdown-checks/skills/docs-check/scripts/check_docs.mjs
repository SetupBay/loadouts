#!/usr/bin/env node
// Offline docs check for Markdown: relative links and images resolve, #fragments match a heading
// (GitHub-style slugs, including in other files), and `npm run <script>` style commands exist in package.json.
// No network: external URLs are left to a scheduled link checker.
//
//   node check_docs.mjs [paths...]     default: README.md and docs/ (when present)
// Exit 0 when clean, 1 when there are problems.
import fs from "node:fs";
import path from "node:path";

const SKIP_DIRS = new Set(["node_modules", ".git", "dist", "build", ".next", "vendor", ".venv"]);
const args = process.argv.slice(2);
const roots = args.length ? args : ["README.md", "docs"].filter((p) => fs.existsSync(p));

function walk(p, out) {
  const st = fs.statSync(p);
  if (st.isDirectory()) {
    for (const e of fs.readdirSync(p)) if (!SKIP_DIRS.has(e)) walk(path.join(p, e), out);
  } else if (/\.mdx?$/i.test(p)) out.push(path.normalize(p));
  return out;
}
const files = roots.flatMap((r) => (fs.existsSync(r) ? walk(r, []) : (console.log(`${r}: not found`), process.exitCode = 1, [])));

// Strip inline Markdown from a heading, then slug it the way GitHub does.
function slug(text) {
  return text
    .replace(/!?\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/`([^`]*)`/g, "$1")
    .replace(/<[^>]+>/g, "")
    .replace(/[*_~]{1,3}(\S[^*_~]*?)[*_~]{1,3}/g, "$1")
    .trim()
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\p{M}\s_-]/gu, "")
    .replace(/\s/g, "-");
}

// Lines outside fenced code blocks, plus the fenced blocks themselves (for command checks).
function parse(file) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/);
  const prose = [];
  const code = [];
  let fence = null;
  lines.forEach((line, i) => {
    const m = line.match(/^\s{0,3}(`{3,}|~{3,})/);
    if (m && !fence) { fence = m[1]; return; }
    if (fence && line.trim().startsWith(fence)) { fence = null; return; }
    (fence ? code : prose).push({ n: i + 1, text: line });
  });
  return { prose, code };
}

const anchorCache = new Map();
function anchors(file) {
  if (anchorCache.has(file)) return anchorCache.get(file);
  const set = new Set();
  const seen = new Map();
  for (const { text } of parse(file).prose) {
    const h = text.match(/^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$/);
    for (const m of text.matchAll(/<a\s+(?:name|id)="([^"]+)"/g)) set.add(m[1]);
    if (!h) continue;
    const base = slug(h[1]);
    const count = seen.get(base) ?? 0;
    seen.set(base, count + 1);
    set.add(count ? `${base}-${count}` : base);
  }
  anchorCache.set(file, set);
  return set;
}

function nearestPackageJson(file) {
  let dir = path.resolve(path.dirname(file));
  for (;;) {
    const p = path.join(dir, "package.json");
    if (fs.existsSync(p)) return p;
    const up = path.dirname(dir);
    if (up === dir) return null;
    dir = up;
  }
}

const problems = [];
let linksChecked = 0;
let commandsChecked = 0;
const report = (file, n, msg) => problems.push(`${file}:${n}: ${msg}`);

for (const file of files) {
  const { prose, code } = parse(file);
  for (const { n, text } of prose) {
    const noCode = text.replace(/`[^`]*`/g, "");
    const targets = [
      ...[...noCode.matchAll(/!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)/g)].map((m) => m[1]),
      ...[...noCode.matchAll(/^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s+.*)?$/g)].map((m) => m[1]),
      ...[...noCode.matchAll(/<(?:img|a)\s[^>]*(?:src|href)="([^"]+)"/g)].map((m) => m[1]),
    ];
    for (const t of targets) {
      if (/^[a-z][a-z0-9+.-]*:/i.test(t) || t.startsWith("//")) continue; // external, mailto:, etc.
      linksChecked++;
      const [rawPath, frag] = t.split("#");
      const decoded = decodeURIComponent(rawPath);
      const target = decoded === "" ? file : decoded.startsWith("/") ? path.normalize(decoded.slice(1)) : path.normalize(path.join(path.dirname(file), decoded));
      if (!fs.existsSync(target)) { report(file, n, `broken link: ${t} (${target} does not exist)`); continue; }
      if (frag !== undefined && /\.mdx?$/i.test(target) && !anchors(target).has(decodeURIComponent(frag).toLowerCase())) {
        report(file, n, `missing anchor: ${t} (no heading "#${frag}" in ${target})`);
      }
    }
  }
  const pkgPath = nearestPackageJson(file);
  const scripts = pkgPath ? Object.keys(JSON.parse(fs.readFileSync(pkgPath, "utf8")).scripts ?? {}) : null;
  const inlineCode = prose.flatMap(({ n, text }) => [...text.matchAll(/`([^`]+)`/g)].map((m) => ({ n, text: m[1] })));
  for (const { n, text } of [...code, ...inlineCode]) {
    for (const m of text.matchAll(/\b(npm|pnpm|yarn|bun)\s+run\s+([\w:.-]+)/g)) {
      commandsChecked++;
      if (!scripts) report(file, n, `"${m[0]}" but no package.json above ${file}`);
      else if (!scripts.includes(m[2])) report(file, n, `"${m[0]}": no "${m[2]}" script in ${path.relative(".", pkgPath)}`);
    }
  }
}

for (const p of problems) console.log(p);
console.log(`docs: ${files.length} files, ${linksChecked} local links, ${commandsChecked} script commands, ${problems.length} problems`);
if (problems.length) process.exitCode = 1;

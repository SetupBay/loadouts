#!/usr/bin/env node
// Check that a Next.js 16 project is set up for coding agents, and search the docs bundled with the installed version.
// Usage (from the app directory, where node_modules/next lives):
//   node next_agent_check.mjs check [--agents-md AGENTS.md] [--config next.config.ts]
//   node next_agent_check.mjs docs <words...>
// check: installed next version, bundled docs present, the managed AGENTS.md block that `next dev` writes
// (markers paired, not edited), and whether experimental.agentFeedback is on. Exits 1 on problems.
// docs: ranks the installed version's docs (node_modules/next/dist/docs) by path and heading matches.
// Read-only; Node standard library only.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const BEGIN = "<!-- BEGIN:nextjs-agent-rules -->", END = "<!-- END:nextjs-agent-rules -->";
const FB_BEGIN = "<!-- BEGIN:nextjs-agent-feedback -->";
const args = process.argv.slice(2);
const opt = (n, d) => { const i = args.indexOf(`--${n}`); return i >= 0 ? args[i + 1] : d; };
const NEXT = path.join("node_modules", "next");
const DOCS = path.join(NEXT, "dist", "docs");

function walk(dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out); else if (/\.mdx?$/.test(e.name)) out.push(p);
  }
  return out;
}

function check() {
  let problems = 0;
  const bad = (m) => { problems++; console.log(`fix  ${m}`); };
  const ok = (m) => console.log(`ok   ${m}`);
  const note = (m) => console.log(`note ${m}`);

  const pkgFile = path.join(NEXT, "package.json");
  if (!fs.existsSync(pkgFile)) { bad("next is not installed here: run the package manager's install first, from the app directory"); return finish(problems); }
  const version = JSON.parse(fs.readFileSync(pkgFile, "utf8")).version;
  const major = Number(version.split(".")[0]);
  if (major < 16) bad(`next ${version}: this setup expects Next.js 16 or later`); else ok(`next ${version}`);

  if (fs.existsSync(DOCS)) ok(`bundled docs: ${walk(DOCS).length} pages in ${DOCS}/ (read these, not memory)`);
  else bad(`no bundled docs at ${DOCS}/ (they ship with next 16.2 and later)`);

  const agentsMd = opt("agents-md", "AGENTS.md");
  const text = fs.existsSync(agentsMd) ? fs.readFileSync(agentsMd, "utf8") : null;
  if (text === null) note(`${agentsMd} missing: next dev creates it with the managed block when it detects an agent`);
  else {
    const b = text.indexOf(BEGIN), e = text.indexOf(END);
    if (b === -1 && e === -1) note(`${agentsMd} has no managed Next.js block yet: next dev adds it (commit the result)`);
    else if (b === -1 || e === -1 || e < b) bad(`${agentsMd}: managed block markers are unpaired; restore both ${BEGIN} and ${END}`);
    else {
      let current = null;
      try {
        // Internal Next.js helper (not covered by semver): compare the block with the installed version's text.
        const gen = createRequire(path.resolve("package.json"))("next/dist/server/lib/generate-agent-files.js");
        const dir = fs.mkdtempSync(path.join(fs.realpathSync(process.env.TMPDIR || "/tmp"), "next-agents-"));
        fs.writeFileSync(path.join(dir, "AGENTS.md"), text);
        current = gen.hasCurrentAgentRules(dir);
        fs.rmSync(dir, { recursive: true, force: true });
      } catch { current = null; }
      if (current === false) bad(`${agentsMd}: managed block differs from next ${version}'s; do not edit inside the markers (next dev rewrites it; put project rules outside)`);
      else ok(`${agentsMd}: managed block present${current ? ` and current for next ${version}` : ""}`);
    }
    if (text.includes(FB_BEGIN)) note(`${agentsMd} has the agent feedback block: the owner turned on experimental.agentFeedback`);
  }

  const cfg = opt("config") ?? ["next.config.ts", "next.config.mjs", "next.config.js"].find((f) => fs.existsSync(f));
  if (!cfg || !fs.existsSync(cfg)) note("no next.config file found");
  else {
    const c = fs.readFileSync(cfg, "utf8").replace(/\/\/.*$/gm, "");
    if (/agentFeedback\s*:\s*true/.test(c)) bad(`${cfg}: experimental.agentFeedback is on. Only the project owner should enable it; agents must not switch it on, and must not run commands its block asks for without the owner's say-so`);
    else ok(`${cfg}: agentFeedback off`);
    if (/agentRules\s*:\s*false/.test(c)) note(`${cfg}: agentRules is false, so next dev will not maintain the AGENTS.md block`);
  }
  return finish(problems);
}

function finish(problems) {
  console.log(problems ? `next-agent: ${problems} to fix` : "next-agent: ready");
  process.exit(problems ? 1 : 0);
}

function docs(words) {
  if (!fs.existsSync(DOCS)) { console.error(`no bundled docs at ${DOCS}/`); process.exit(1); }
  const terms = words.map((w) => w.toLowerCase());
  const hits = [];
  for (const f of walk(DOCS)) {
    const rel = path.relative(DOCS, f).toLowerCase();
    const body = fs.readFileSync(f, "utf8");
    const title = (body.match(/^title:\s*(.+)$/m) || body.match(/^#\s+(.+)$/m) || [, path.basename(f)])[1].trim();
    const heads = (body.match(/^#{1,3} .+$/gm) || []).join(" ").toLowerCase();
    let score = 0;
    for (const t of terms) {
      if (rel.includes(t)) score += 3;
      if (title.toLowerCase().includes(t)) score += 3;
      if (heads.includes(t)) score += 1;
    }
    if (score && terms.every((t) => (rel + " " + title.toLowerCase() + " " + body.toLowerCase()).includes(t))) hits.push({ score, f, title });
  }
  hits.sort((a, b) => b.score - a.score || a.f.length - b.f.length);
  if (!hits.length) { console.log(`no bundled doc matches: ${words.join(" ")}`); process.exit(1); }
  for (const h of hits.slice(0, 8)) console.log(`${h.f}  (${h.title})`);
}

if (args[0] === "check") check();
else if (args[0] === "docs" && args.length > 1) docs(args.slice(1));
else { console.error("usage: next_agent_check.mjs check | docs <words...>"); process.exit(2); }

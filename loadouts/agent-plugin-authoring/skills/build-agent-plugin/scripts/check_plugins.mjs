#!/usr/bin/env node
// Check the built plugins for what the agents' own validators miss or do not cover.
// Usage: node check_plugins.mjs [dist-plugins]
// Antigravity has no validate command, so its manifest is checked against the schema
// published in its docs. Claude Code output is checked for parity; run
// `claude plugin validate <dir> --strict` as well. Exit 1 on any ERROR.
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const out = process.argv[2] ?? "dist-plugins";
let errors = 0;
const err = (m) => { errors++; console.log(`ERROR ${m}`); };
const ok = (m) => console.log(`ok    ${m}`);
const readJson = (p) => JSON.parse(readFileSync(p, "utf8"));

function frontmatter(text) {
  const m = /^---\n([\s\S]*?)\n---\n/.exec(text);
  if (!m) return null;
  const fm = {};
  for (const line of m[1].split("\n")) {
    const kv = /^([A-Za-z][\w-]*):\s*(.*)$/.exec(line);
    if (kv) fm[kv[1]] = kv[2].replace(/^["']|["']$/g, "");
  }
  return fm;
}

function* files(dir) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) yield* files(p); else yield p;
  }
}

function checkSkillsAndAgents(root, label) {
  const skills = [];
  if (existsSync(join(root, "skills"))) {
    for (const name of readdirSync(join(root, "skills"))) {
      const p = join(root, "skills", name, "SKILL.md");
      if (!existsSync(p)) { err(`${label}: skills/${name} has no SKILL.md`); continue; }
      const fm = frontmatter(readFileSync(p, "utf8"));
      if (!fm) { err(`${label}: skills/${name}/SKILL.md has no frontmatter`); continue; }
      if (fm.name && fm.name !== name) err(`${label}: skills/${name} frontmatter name is "${fm.name}"`);
      if (!fm.description || fm.description.length < 20) err(`${label}: skills/${name} needs a description that says when to use it`);
      skills.push(name);
    }
  }
  const agents = [];
  if (existsSync(join(root, "agents"))) {
    for (const name of readdirSync(join(root, "agents")).filter((n) => n.endsWith(".md"))) {
      const fm = frontmatter(readFileSync(join(root, "agents", name), "utf8"));
      if (!fm?.name || !fm?.description) err(`${label}: agents/${name} needs name and description (Antigravity requires both)`);
      agents.push(name);
    }
  }
  return { skills, agents };
}

const PIN = { npx: /@\d+\.\d+\.\d+$/, uvx: /==\d+(\.\d+)*$|@\d+(\.\d+)+$/ };
function checkServers(file, label, remoteKey) {
  if (!existsSync(file)) return [];
  const { mcpServers = {} } = readJson(file);
  for (const [name, s] of Object.entries(mcpServers)) {
    if (s.command === "npx" || s.command === "uvx") {
      const pkg = (s.args ?? []).find((a) => !a.startsWith("-"));
      if (!pkg || !PIN[s.command].test(pkg)) err(`${label}: MCP server ${name} runs ${s.command} ${pkg ?? ""} without an exact version`);
    }
    if (remoteKey === "serverUrl" && (s.url || s.httpUrl)) err(`${label}: MCP server ${name} uses url/httpUrl; Antigravity reads serverUrl only`);
    if (remoteKey === "url" && s.serverUrl) err(`${label}: MCP server ${name} uses serverUrl; Claude Code reads url`);
    const remote = s[remoteKey];
    if (remote && !remote.startsWith("https://")) err(`${label}: MCP server ${name} remote URL is not https`);
    for (const [k, v] of Object.entries({ ...(s.env ?? {}), ...(s.headers ?? {}) })) {
      if (typeof v === "string" && !/\$\{[A-Za-z_][\w.]*\}/.test(v) && /token|key|secret|auth|bearer/i.test(k + v)) {
        err(`${label}: MCP server ${name} ${k} looks like a literal credential; reference an environment variable`);
      }
    }
  }
  return Object.keys(mcpServers);
}

const ccRoot = join(out, "claude");
const agRoot = join(out, "antigravity");
const names = existsSync(agRoot) ? readdirSync(agRoot) : [];
if (!names.length) err(`no plugins under ${agRoot}`);

for (const name of names) {
  const ag = join(agRoot, name);
  const cc = join(ccRoot, name);
  const before = errors;

  // Antigravity manifest: the documented schema has additionalProperties false.
  const m = readJson(join(ag, "plugin.json"));
  const allowed = new Set(["$schema", "name", "description"]);
  const extra = Object.keys(m).filter((k) => !allowed.has(k));
  if (extra.length) err(`antigravity/${name}/plugin.json: fields not in the schema: ${extra.join(", ")}`);
  if (!/^[a-zA-Z0-9-_]+$/.test(m.name ?? "")) err(`antigravity/${name}/plugin.json: name must match ^[a-zA-Z0-9-_]+$ (the CLI requires it)`);
  if (m.name !== name) err(`antigravity/${name}: folder name and manifest name differ`);
  if (existsSync(join(ag, ".claude-plugin"))) err(`antigravity/${name}: contains .claude-plugin/`);

  // Claude Code manifest basics (claude plugin validate --strict covers the rest).
  const c = readJson(join(cc, ".claude-plugin", "plugin.json"));
  if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(c.name)) err(`claude/${name}: name should be kebab-case`);
  if (/^(claude|anthropic|anthropics|cc-plugin)-/i.test(c.name)) err(`claude/${name}: name is reserved for Anthropic`);
  for (const k of ["version", "description", "author"]) if (!c[k]) err(`claude/${name}: ${k} missing (--strict fails)`);
  if (existsSync(join(cc, "CLAUDE.md"))) err(`claude/${name}: a CLAUDE.md at the plugin root is not loaded; use a skill`);
  if (existsSync(join(cc, "plugin.json"))) err(`claude/${name}: plugin.json belongs in .claude-plugin/`);

  // Same components on both sides.
  const a = checkSkillsAndAgents(ag, `antigravity/${name}`);
  const b = checkSkillsAndAgents(cc, `claude/${name}`);
  if (JSON.stringify(a) !== JSON.stringify(b)) err(`${name}: skills or agents differ between the two builds`);
  const sa = checkServers(join(ag, "mcp_config.json"), `antigravity/${name}`, "serverUrl");
  const sb = checkServers(join(cc, ".mcp.json"), `claude/${name}`, "url");
  if (JSON.stringify(sa) !== JSON.stringify(sb)) err(`${name}: MCP servers differ between the two builds`);

  // Nothing that escapes the plugin root or depends on one agent's variables in shared files.
  for (const f of [...files(ag)]) {
    const text = readFileSync(f, "utf8");
    if (text.includes("${CLAUDE_PLUGIN_ROOT}")) err(`antigravity/${name}/${relative(ag, f)}: uses \${CLAUDE_PLUGIN_ROOT}, which only Claude Code substitutes`);
    if (/\.\.\//.test(text) && f.endsWith(".json")) err(`antigravity/${name}/${relative(ag, f)}: path with ../`);
  }

  if (errors === before) ok(`${name}: ${a.skills.length} skill(s), ${a.agents.length} agent(s), ${sa.length} MCP server(s) in both builds`);
}

console.log(errors ? `${errors} error(s)` : "plugins ok");
process.exit(errors ? 1 : 0);

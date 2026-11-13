#!/usr/bin/env node
// Build a Claude Code plugin and an Antigravity plugin from one source tree.
// Usage: node build_plugins.mjs [plugin-src] [out]   (defaults: plugin-src, dist-plugins)
//
// plugin-src/
//   plugin.json        name, version, description, author, license, repository, mcpServers
//   skills/<name>/SKILL.md (+ supporting files)  copied to both
//   agents/<name>.md   frontmatter with name and description only (portable), then the body
//
// Output:
//   out/claude/.claude-plugin/marketplace.json   a one-plugin marketplace for local testing
//   out/claude/<name>/.claude-plugin/plugin.json, skills/, agents/, .mcp.json
//   out/antigravity/<name>/plugin.json, skills/, agents/, mcp_config.json
import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const src = process.argv[2] ?? "plugin-src";
const out = process.argv[3] ?? "dist-plugins";
const meta = JSON.parse(readFileSync(join(src, "plugin.json"), "utf8"));
for (const k of ["name", "version", "description"]) {
  if (!meta[k]) throw new Error(`plugin-src/plugin.json: ${k} is required`);
}
const write = (p, obj) => { mkdirSync(join(p, ".."), { recursive: true }); writeFileSync(p, JSON.stringify(obj, null, 2) + "\n"); };

rmSync(out, { recursive: true, force: true });
const cc = join(out, "claude", meta.name);
const ag = join(out, "antigravity", meta.name);

for (const dir of [cc, ag]) {
  mkdirSync(dir, { recursive: true });
  for (const part of ["skills", "agents"]) {
    if (existsSync(join(src, part))) cpSync(join(src, part), join(dir, part), { recursive: true });
  }
}

// Claude Code: manifest in .claude-plugin/, MCP in .mcp.json, remote servers use type + url.
const ccManifest = {
  name: meta.name,
  version: meta.version,
  description: meta.description,
  ...(meta.author ? { author: meta.author } : {}),
  ...(meta.license ? { license: meta.license } : {}),
  ...(meta.repository ? { repository: meta.repository } : {}),
  ...(meta.keywords ? { keywords: meta.keywords } : {}),
};
write(join(cc, ".claude-plugin", "plugin.json"), ccManifest);

// Antigravity: plugin.json at the root, and its schema allows only name and description.
write(join(ag, "plugin.json"), {
  $schema: "https://antigravity.google/schemas/v1/plugin.json",
  name: meta.name,
  description: meta.description,
});

const servers = meta.mcpServers ?? {};
if (Object.keys(servers).length) {
  const ccServers = {};
  const agServers = {};
  for (const [name, s] of Object.entries(servers)) {
    if (s.url) {
      ccServers[name] = { type: "http", url: s.url, ...(s.headers ? { headers: s.headers } : {}) };
      agServers[name] = { serverUrl: s.url, ...(s.headers ? { headers: s.headers } : {}) };
    } else {
      const local = { command: s.command, ...(s.args ? { args: s.args } : {}), ...(s.env ? { env: s.env } : {}) };
      ccServers[name] = local;
      agServers[name] = local;
    }
  }
  write(join(cc, ".mcp.json"), { mcpServers: ccServers });
  write(join(ag, "mcp_config.json"), { mcpServers: agServers });
}

// A local marketplace so `claude plugin validate` and a test install see the real layout.
write(join(out, "claude", ".claude-plugin", "marketplace.json"), {
  name: `${meta.name}-dev`,
  description: `Local development marketplace for ${meta.name}.`,
  owner: meta.author ?? { name: "unknown" },
  plugins: [{ name: meta.name, source: `./${meta.name}`, description: meta.description }],
});

console.log(`built ${meta.name} ${meta.version}: ${join(out, "claude", meta.name)} and ${ag}`);

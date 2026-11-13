#!/usr/bin/env node
// Find MCP server code that protocol revision 2026-07-28 removed or changed.
// Usage: node scan_mcp_legacy.mjs [dir ...]   (default: .)
// Prints file:line, what changed and what to do. Exit 1 if anything is found.
// Patterns are plain strings joined at runtime so this file does not flag itself.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, extname, basename } from "node:path";

const j = (...parts) => parts.join("");
const RULES = [
  { re: new RegExp(j("Mcp-Session", "-Id|session", "IdGenerator|\\bsession", "Id\\b"), "i"),
    what: "Sessions are gone; there is no Mcp-Session-Id.",
    fix: "Pass state the next call needs in tool arguments (a server-minted handle) or, inside one multi-round-trip call, in an integrity-protected requestState." },
  { re: new RegExp(j("[\"']notifications/", "initialized[\"']|on", "initialized\\b|[\"']initi", "alize[\"']")),
    what: "The initialize/initialized handshake is removed; every request carries _meta with protocolVersion and clientCapabilities.",
    fix: "Let the SDK's 2026 entry point (serveStdio / createMcpHandler, MCPServer v2, go-sdk >= v1.7.0) handle eras. Do not hand-roll handshake handlers." },
  { re: new RegExp(j("[\"']pi", "ng[\"']")), what: "ping is removed.", fix: "Delete ping handlers and keep-alive pings." },
  { re: new RegExp(j("logging/set", "Level|set", "LoggingLevel|send", "LoggingMessage")),
    what: "logging/setLevel is removed and protocol logging is deprecated.",
    fix: "Log to stderr (stdio) or OpenTelemetry. If you keep protocol logs, read the per-request io.modelcontextprotocol/logLevel." },
  { re: new RegExp(j("sampling/create", "Message|\\.create", "Message\\(|request", "Sampling\\(")),
    what: "Server-to-client sampling requests are gone (sampling is deprecated).",
    fix: "Return input_required with a sampling/createMessage entry in inputRequests, or drop the dependency on client-side LLM calls." },
  { re: new RegExp(j("elicit", "Input\\(|(?<!input", "Required)\\.elicit\\(")),
    what: "Server-pushed elicitation is gone.",
    fix: "Return input_required with an elicitation/create entry in inputRequests and read inputResponses on the retry." },
  { re: new RegExp(j("roots/li", "st|list", "Roots\\(|notifications/roots/list_", "changed")),
    what: "Roots are deprecated and roots/list_changed is removed.",
    fix: "Take the paths a tool needs as tool arguments, checked against an allowed root." },
  { re: new RegExp(j("resources/sub", "scribe|resources/unsub", "scribe")),
    what: "resources/subscribe and resources/unsubscribe are replaced.",
    fix: "Use subscriptions/listen (the long-lived stream that also replaced the HTTP GET endpoint)." },
  { re: new RegExp(j("Last-Event", "-ID|event", "Store\\b|Event", "Store\\b"), "i"),
    what: "SSE resumability (Last-Event-ID, event stores) is removed.",
    fix: "Drop the event store; long work belongs in the tasks extension or a handle the client can poll." },
  { re: new RegExp(j("-3200", "2\\b")),
    what: "Resource not found is now -32602 (invalid params), not -32002.",
    fix: "Return -32602 for an unknown resource URI." },
  { re: new RegExp(j("SSEServer", "Transport|sse_", "app\\(")),
    what: "The HTTP+SSE transport is deprecated.",
    fix: "Serve Streamable HTTP (createMcpHandler in TypeScript v2)." },
  { re: new RegExp(j("Stdio", "ServerTransport\\(")),
    what: "A v2 TypeScript McpServer connected straight to StdioServerTransport only speaks 2025-era protocol.",
    fix: "Replace server.connect(new StdioServerTransport()) with serveStdio(() => buildServer())." },
  { re: new RegExp(j("@modelcontext", "protocol/sdk\\b")),
    what: "@modelcontextprotocol/sdk is the v1 TypeScript SDK; v1 never speaks 2026-07-28.",
    fix: "Run npx @modelcontextprotocol/codemod@2.3.1 v1-to-v2 . then pin @modelcontextprotocol/server 2.3.1." },
  { re: new RegExp(j("mcp\\.server\\.fast", "mcp|\\bmcp\\s*(==|~=|<)\\s*1\\.")),
    what: "MCP Python SDK v1 (FastMCP) does not speak 2026-07-28.",
    fix: "Pin mcp==2.3.0 and use from mcp.server import MCPServer." },
  { re: new RegExp(j("modelcontextprotocol/go-", "sdk v(0\\.|1\\.[0-6]\\.)")),
    what: "go-sdk before v1.7.0 does not speak 2026-07-28.",
    fix: "go get github.com/modelcontextprotocol/go-sdk@v1.8.0" },
  { re: new RegExp(j("[\"']tasks/(get|list|cancel|res", "ult)[\"']")),
    what: "Tasks moved out of core into the io.modelcontextprotocol/tasks extension.",
    fix: "Advertise the extension under capabilities.extensions and follow its spec, or drop task support." },
];

const EXT = new Set([".ts", ".mts", ".cts", ".js", ".mjs", ".cjs", ".py", ".go", ".rs", ".json", ".toml", ".txt", ".mod"]);
const SKIP = new Set(["node_modules", ".git", "dist", "build", ".venv", "venv", "__pycache__", "vendor", "target"]);
const self = basename(new URL(import.meta.url).pathname);
const lockfiles = new Set(["package-lock.json", "pnpm-lock.yaml", "yarn.lock", "uv.lock", "go.sum", "Cargo.lock"]);

function* walk(p) {
  const st = statSync(p);
  if (st.isFile()) { yield p; return; }
  for (const name of readdirSync(p)) {
    if (SKIP.has(name)) continue;
    yield* walk(join(p, name));
  }
}

let hits = 0;
const roots = process.argv.slice(2).length ? process.argv.slice(2) : ["."];
for (const root of roots) {
  for (const file of walk(root)) {
    const name = basename(file);
    if (name === self || lockfiles.has(name)) continue;
    if (!EXT.has(extname(file)) && name !== "requirements.txt") continue;
    const lines = readFileSync(file, "utf8").split("\n");
    lines.forEach((line, i) => {
      if (/^\s*(\/\/|#|\*|\/\*)/.test(line)) return; // comments describe the old way; skip them
      for (const r of RULES) {
        if (r.re.test(line)) {
          hits++;
          console.log(`${file}:${i + 1}: ${r.what}\n    fix: ${r.fix}`);
        }
      }
    });
  }
}
console.log(hits ? `${hits} finding(s)` : "no 2025-era MCP patterns found");
process.exit(hits ? 1 : 0);

#!/usr/bin/env node
// Probe a stdio MCP server for protocol revision 2026-07-28 behaviour.
// Usage: node probe_mcp_2026.mjs [--call <tool> '<json args>' [--answer '<inputResponses json>']] -- <command> [args...]
// --answer: if the call returns input_required, retry once with these inputResponses
// (the probe declares the elicitation capability on the call so the server may ask).
// No dependencies. Exit 1 if a MUST-level check fails.
import { spawn } from "node:child_process";

const MODERN = "2026-07-28";
const argv = process.argv.slice(2);
const sep = argv.indexOf("--");
if (sep === -1 || sep === argv.length - 1) {
  console.error("usage: probe_mcp_2026.mjs [--call <tool> '<json>'] -- <command> [args...]");
  process.exit(2);
}
const opts = argv.slice(0, sep);
const cmd = argv.slice(sep + 1);
let call = null;
const ci = opts.indexOf("--call");
if (ci !== -1) call = { name: opts[ci + 1], args: JSON.parse(opts[ci + 2] ?? "{}") };
const ai = opts.indexOf("--answer");
const answer = ai !== -1 ? JSON.parse(opts[ai + 1]) : null;

const envelope = (version = MODERN, caps = {}) => ({
  "io.modelcontextprotocol/protocolVersion": version,
  "io.modelcontextprotocol/clientInfo": { name: "probe-mcp-2026", version: "1.0.0" },
  "io.modelcontextprotocol/clientCapabilities": caps,
});

let failures = 0;
const pass = (m) => console.log(`PASS ${m}`);
const fail = (m) => { failures++; console.log(`FAIL ${m}`); };
const warn = (m) => console.log(`WARN ${m}`);
const info = (m) => console.log(`INFO ${m}`);

function startServer() {
  const child = spawn(cmd[0], cmd.slice(1), { stdio: ["pipe", "pipe", "pipe"] });
  const pending = new Map();
  const nonJson = [];
  let buf = "";
  child.stdout.setEncoding("utf8");
  child.stdout.on("data", (chunk) => {
    buf += chunk;
    let i;
    while ((i = buf.indexOf("\n")) !== -1) {
      const line = buf.slice(0, i).trim();
      buf = buf.slice(i + 1);
      if (!line) continue;
      let msg;
      try { msg = JSON.parse(line); } catch { nonJson.push(line); continue; }
      if (msg.id !== undefined && pending.has(msg.id)) {
        pending.get(msg.id)(msg);
        pending.delete(msg.id);
      }
    }
  });
  child.stderr.resume();
  let next = 1;
  const request = (method, params, timeoutMs = 15000) =>
    new Promise((resolve) => {
      const id = next++;
      const timer = setTimeout(() => { pending.delete(id); resolve({ timeout: true }); }, timeoutMs);
      pending.set(id, (msg) => { clearTimeout(timer); resolve(msg); });
      child.stdin.write(JSON.stringify({ jsonrpc: "2.0", id, method, params }) + "\n");
    });
  const stop = () => { child.stdin.end(); setTimeout(() => child.kill(), 500).unref(); };
  return { request, stop, nonJson };
}

function checkMismatch(label, msg, onMiss = fail) {
  if (msg.error?.code === -32022 && Array.isArray(msg.error.data?.supported))
    pass(`${label} -> -32022, supported ${JSON.stringify(msg.error.data.supported)}`);
  else {
    const got = msg.timeout ? "no answer" : JSON.stringify(msg.error ?? { result: Object.keys(msg.result ?? {}) });
    onMiss(`${label}: expected error -32022 with data.supported, got ${got.slice(0, 160)}`);
  }
}

const names = (msg) => (msg.result?.tools ?? []).map((t) => t.name);

async function main() {
  const s = startServer();

  // 1. server/discover (servers MUST implement it)
  const d = await s.request("server/discover", { _meta: envelope() });
  if (d.timeout) fail("server/discover: no answer (a legacy-only server, or it waits for initialize)");
  else if (d.error) fail(`server/discover: error ${d.error.code} ${d.error.message}`);
  else {
    const r = d.result;
    if (r.resultType === "complete") pass("server/discover: resultType complete");
    else fail(`server/discover: resultType is ${JSON.stringify(r.resultType)}, expected "complete"`);
    const versions = r.supportedVersions ?? [];
    if (versions.includes(MODERN)) pass(`server/discover: supportedVersions ${JSON.stringify(versions)}`);
    else fail(`server/discover: supportedVersions ${JSON.stringify(versions)} does not include ${MODERN}`);
    const si = r._meta?.["io.modelcontextprotocol/serverInfo"];
    if (si?.name) pass(`server/discover: serverInfo ${si.name} ${si.version ?? ""}`.trim());
    else warn("server/discover: no io.modelcontextprotocol/serverInfo in result _meta (SHOULD)");
    info(`capabilities: ${Object.keys(r.capabilities ?? {}).join(", ") || "none"}`);
  }

  // 2. stateless tools/list, twice: no handshake, deterministic order
  const l1 = await s.request("tools/list", { _meta: envelope() });
  const l2 = await s.request("tools/list", { _meta: envelope() });
  if (l1.timeout || l1.error) fail(`tools/list with _meta and no initialize: ${l1.error ? l1.error.message : "no answer"}`);
  else {
    if (l1.result.resultType === "complete") pass(`tools/list stateless: ${names(l1).join(", ") || "(no tools)"}`);
    else fail(`tools/list: resultType is ${JSON.stringify(l1.result.resultType)}, expected "complete"`);
    if (JSON.stringify(names(l1)) === JSON.stringify(names(l2))) pass("tools/list order is stable across calls");
    else fail("tools/list order changed between two identical calls (MUST be deterministic)");
    if ("ttlMs" in l1.result || "cacheScope" in l1.result) info(`cache hints: ttlMs=${l1.result.ttlMs} cacheScope=${l1.result.cacheScope}`);
    else info("no ttlMs/cacheScope cache hints on tools/list (optional)");
  }

  // 3. optional tools/call, with one multi-round-trip retry if --answer is given
  if (call) {
    const caps = { elicitation: {} };
    const params = { name: call.name, arguments: call.args, _meta: envelope(MODERN, caps) };
    let c = await s.request("tools/call", params);
    if (!c.timeout && !c.error && c.result.resultType === "input_required") {
      const keys = Object.keys(c.result.inputRequests ?? {});
      pass(`tools/call ${call.name}: input_required asks for ${keys.join(", ") || "(requestState only)"}`);
      if (answer) {
        const retry = { ...params, inputResponses: answer, _meta: envelope(MODERN, caps) };
        if (c.result.requestState !== undefined) retry.requestState = c.result.requestState;
        c = await s.request("tools/call", retry);
      }
    }
    if (c.timeout || c.error) fail(`tools/call ${call.name}: ${c.error ? c.error.message : "no answer"}`);
    else if (c.result.resultType === "input_required") info(`tools/call ${call.name}: still input_required`);
    else if (c.result.resultType === "complete" && !c.result.isError)
      pass(`tools/call ${call.name}: complete: ${(c.result.content?.[0]?.text ?? "").slice(0, 80)}`);
    else fail(`tools/call ${call.name}: resultType ${c.result.resultType} isError ${c.result.isError}`);
  }

  // 4. unknown version on an established connection. The spec says every request
  // carries its version and an unsupported one MUST get -32022, but the official
  // TypeScript and Go SDKs pin the era per stdio connection, so this is a warning.
  const bad = await s.request("tools/list", { _meta: envelope("1900-01-01") });
  checkMismatch("unknown version mid-connection", bad, warn);
  s.stop();
  if (s.nonJson.length) fail(`stdout carried ${s.nonJson.length} non-JSON line(s), first: ${s.nonJson[0].slice(0, 80)}`);
  else pass("stdout carried only JSON-RPC");

  // 5. legacy initialize in a fresh process: dual-era or modern-only?
  const l = startServer();
  const init = await l.request("initialize", {
    protocolVersion: "2025-11-25",
    capabilities: {},
    clientInfo: { name: "probe-mcp-2026-legacy", version: "1.0.0" },
  }, 8000);
  l.stop();
  if (init.result?.protocolVersion) info(`era: dual-era (legacy initialize negotiated ${init.result.protocolVersion})`);
  else if (init.error) {
    info("era: modern-only (legacy initialize rejected)");
    if (!/20\d\d-\d\d-\d\d/.test(init.error.message + JSON.stringify(init.error.data ?? ""))) warn("initialize error does not name the supported versions (SHOULD)");
  } else warn("legacy initialize got no answer");

  // 6. unknown version on the opening probe of a fresh process MUST also be -32022
  const f = startServer();
  const fresh = await f.request("server/discover", { _meta: envelope("1900-01-01") }, 8000);
  f.stop();
  checkMismatch("unknown version on the opening server/discover", fresh);

  console.log(failures ? `RESULT: ${failures} failure(s)` : `RESULT: speaks ${MODERN}`);
  process.exit(failures ? 1 : 0);
}

main();

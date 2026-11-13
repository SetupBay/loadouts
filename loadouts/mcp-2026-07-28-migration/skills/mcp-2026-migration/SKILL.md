---
name: mcp-2026-migration
description: Move an MCP server to protocol revision 2026-07-28 (stateless requests, server/discover, input_required) on the official TypeScript, Python or Go SDK, then prove it with a raw stdio probe. Use when upgrading an MCP SDK, removing sessions or initialize handling, or when a 2026 client cannot talk to the server.
---

# Migrate an MCP server to 2026-07-28

Revision 2026-07-28 makes MCP stateless: no `initialize` handshake, no sessions, every request carries its own
`_meta` envelope, and servers can no longer push requests to the client mid-call. `references/changes.md` lists
every change with its fix. Read it before editing.

## 1. Find what has to change

```bash
node scripts/scan_mcp_legacy.mjs .
```

Each finding names the line, what the revision changed and the fix. Lockfiles, `node_modules`, `dist` and comments
are skipped. Work through the findings; do not delete a feature to make the scan clean without asking.

## 2. Upgrade the SDK (exact pins)

| SDK | 2026-07-28 from | Pin | Serving entry |
| --- | --- | --- | --- |
| TypeScript | v2 packages | `@modelcontextprotocol/server@2.3.1` | `serveStdio(() => buildServer())`, `createMcpHandler(factory)` for HTTP |
| Python | `mcp` 2.x | `mcp==2.3.0` | `MCPServer(...).run()`, dual-era by default |
| Go | go-sdk v1.7.0 | `github.com/modelcontextprotocol/go-sdk@v1.8.0` | `mcp.NewServer` + `server.Run(ctx, &mcp.StdioTransport{})` |

TypeScript v1 (`@modelcontextprotocol/sdk`) never speaks 2026-07-28. Run the official codemod at the package root,
then fix what it marks:

```bash
npx @modelcontextprotocol/codemod@2.3.1 v1-to-v2 .
grep -rn '@mcp-codemod-error' . --exclude-dir=node_modules
npx tsc --noEmit
```

On TypeScript v2 a server wired with `server.connect(new StdioServerTransport())` still speaks only the 2025 era.
Switching to `serveStdio(buildServer)` is the opt-in. `references/server.ts` is a complete example.

## 3. Rewrite the removed patterns

- **Session state** becomes explicit: return a handle (an id the server minted) and take it back as a tool
  argument. Inside one multi-round-trip call, carry state in `requestState`, and sign it (the TypeScript SDK's
  `createRequestStateCodec`), because it comes back from the client.
- **elicitInput / createMessage / listRoots** inside a tool become an `input_required` result. The handler returns
  `inputRequired({ inputRequests: { key: inputRequired.elicit({...}) } })`, the client retries the same call with
  `inputResponses`, and the handler runs again and reads the answer (`acceptedContent(...)` in TypeScript).
  Treat `inputResponses` as untrusted and validate them.
- **Logging**: write to stderr. `logging/setLevel` is gone; a modern request may carry
  `io.modelcontextprotocol/logLevel`, and when it does not, protocol log notifications are not sent.
- **Subscriptions**: `resources/subscribe` becomes `subscriptions/listen`.
- **Errors**: unknown resource is `-32602`. Unsupported version is `-32022`, and the SDK sends it.
- **Ordering**: register tools in a fixed order. `tools/list` must be deterministic.

Keep 2025-era clients working unless the user says otherwise. All three SDKs serve both eras from one server by
default. Modern-only is an opt-in (`{ legacy: 'reject' }` in TypeScript).

## 4. Prove it on the wire

Build, then probe the real server command over stdio:

```bash
node scripts/probe_mcp_2026.mjs -- node dist/server.js
node scripts/probe_mcp_2026.mjs --call delete_note '{"id":"n1"}' \
  --answer '{"confirm":{"action":"accept","content":{"confirm":true}}}' -- node dist/server.js
```

The probe sends `server/discover` and stateless `tools/list` calls with the `_meta` envelope. It checks `resultType`,
`serverInfo`, stable tool order, `-32022` for an unknown version, and that stdout is pure JSON-RPC. It runs one
`input_required` round trip if asked, and reports whether a legacy `initialize` still works (dual-era) or not. `FAIL`
lines are MUST-level and the exit code is 1.

On an established stdio connection the official TypeScript and Go SDKs pin the era, so a request with an unknown
version mid-connection is served rather than rejected. The probe reports that as `WARN`. The Go SDK v1.8.0 also
answers an unknown-version opening `server/discover` with method-not-found, not `-32022`, and the probe fails it.
That is SDK behaviour: note it in the PR and check the go-sdk issue tracker. Do not hand-roll the wire format.

## Done means

- The scan is clean, or every remaining finding is explained in the PR.
- The SDK is pinned exactly and the lockfile is committed.
- The probe prints `RESULT: speaks 2026-07-28`.
- The existing tests pass, including legacy-client tests if the server stays dual-era.

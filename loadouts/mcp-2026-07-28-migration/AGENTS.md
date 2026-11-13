# AGENTS.md: MCP server migrating to protocol 2026-07-28

This MCP server is moving to protocol revision 2026-07-28: stateless requests with a per-request `_meta` envelope,
`server/discover`, and `input_required` results instead of server-to-client requests. The spec at
https://modelcontextprotocol.io/specification/2026-07-28 is the authority. Do not rely on memory of older revisions,
which had sessions and an `initialize` handshake.

## How to work
- Start with the `mcp-2026-migration` skill. Scan first, then change code, then prove it with the skill's probe
  against the built server.
- Upgrade through the official SDK, never by hand-writing JSON-RPC: TypeScript `@modelcontextprotocol/server`
  2.3.1, Python `mcp==2.3.0`, Go `github.com/modelcontextprotocol/go-sdk` v1.8.0. Pin exactly and commit the
  lockfile.
- TypeScript v1 (`@modelcontextprotocol/sdk`): run the official codemod first, then fix what it marks.
- Keep 2025-era clients working (dual-era) unless the user decides otherwise. Ask before going modern-only.

## Rules
- No state keyed on a session or connection. Anything a later call needs goes back to the client as a handle or,
  within one call, as signed `requestState`.
- `inputResponses` and `requestState` come from the client: validate them, and never let them grant access.
- stdout is the protocol on stdio. Logs go to stderr.
- Register tools in a fixed order. Return `-32602` for an unknown resource.
- Destructive tools ask for confirmation through `input_required`, not by assuming the client will prompt.

## Done means
- The skill's scanner is clean, or each remaining finding is explained.
- The probe prints `RESULT: speaks 2026-07-28`.
- Type-check, lint and the existing tests pass.

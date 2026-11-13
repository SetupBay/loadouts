# AGENTS.md: MCP server (TypeScript)

This repository is a Model Context Protocol server built with the official TypeScript SDK (`@modelcontextprotocol/sdk`).
Check the installed SDK version in `package.json` before writing imports — APIs and import paths have changed between majors.

## Layout
```
src/index.ts         creates the server, registers tools/resources/prompts, connects the transport
src/tools/<name>.ts  one tool per file: exports a register(server) function
src/lib/             API clients and shared helpers
```

## Transport
- **stdio** for local servers launched by the agent. **stdout belongs to the protocol.** Never `console.log` —
  log with `console.error` (stderr) or a logger pointed at stderr. A stray print corrupts the JSON-RPC stream.
- **Streamable HTTP** for remote servers. Require auth (bearer token or OAuth) for anything non-public, validate the
  `Origin` header, and bind to `127.0.0.1` when running locally.

## Tool design (this is the product)
- The model chooses tools from their **name and description alone**. Write descriptions for the model: what it does,
  when to use it, what it returns, and any important limits. One to three sentences.
- Names: `snake_case`, verb first, specific: `search_issues`, `get_issue`, `create_issue_comment`. Not `issues` or `do_action`.
- Few, focused tools beat many overlapping ones. If two tools are often confused, merge them or sharpen the descriptions.
- Inputs: small, typed zod schemas with `.describe()` on every field. Use enums for fixed choices, sensible defaults, and bounded numbers (`limit` 1–50).
- Outputs: concise text the model can use. Return the fields that matter, not the whole raw API response.
  Paginate or truncate large results and say so in the output ("showing 20 of 312; pass cursor=... for more").
- Mark read-only tools with the `readOnlyHint` annotation and destructive ones with `destructiveHint`.

## Errors and safety
- Validate inputs (the SDK validates against the zod schema; add business checks on top).
- Expected failures (not found, rate limited, bad input) are returned as a tool result with `isError: true` and a message
  the model can act on ("No issue #42 in repo x/y. Use search_issues to find valid numbers."). Do not throw for them.
- Secrets (API keys) come from environment variables passed in the client's MCP config. Never return them in output.
- Treat content fetched from the outside world as untrusted: return it as data, never execute it.
- Destructive tools should require an explicit confirmation field or be left out of v1.

## Testing
- `npm run build`, then `npx @modelcontextprotocol/inspector node dist/index.js` to list and call tools by hand.
- Unit-test tool handlers as plain functions, separately from the transport.

## Before you say "done"
Build passes, the new tool shows up in the Inspector with a clear description, and you have called it at least once with valid and invalid input.

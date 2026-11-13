# MCP 2026-07-28: what changed for servers

Source: the official changelog at https://modelcontextprotocol.io/specification/2026-07-28/changelog and the
versioning, discover, multi-round-trip and stdio pages of the same spec. Check there before relying on a detail.

## Removed or replaced

| 2025-11-25 and earlier | 2026-07-28 | Server action |
| --- | --- | --- |
| `initialize` / `notifications/initialized` handshake | Every request carries `_meta` with `io.modelcontextprotocol/protocolVersion` and `io.modelcontextprotocol/clientCapabilities` (clientInfo SHOULD) | Use the SDK's 2026 entry point; no handshake code |
| Version negotiated once | Per request; unsupported version gets `UnsupportedProtocolVersionError` `-32022` with `data.supported` | Let the SDK answer |
| (none) | `server/discover` returns `supportedVersions`, `capabilities`, `instructions`, serverInfo in result `_meta` | Servers MUST implement it (SDKs do) |
| `Mcp-Session-Id` and session state | No sessions | Handles in tool arguments; `requestState` within one call |
| Server-to-client `sampling/createMessage`, `elicitation/create`, `roots/list` | `InputRequiredResult` (`resultType: "input_required"`, `inputRequests`, optional `requestState`); client retries with `inputResponses` | Only on `tools/call`, `prompts/get`, `resources/read` |
| `ping` | Removed | Delete handlers |
| `logging/setLevel` | Per-request `io.modelcontextprotocol/logLevel`; logging deprecated | stderr or OpenTelemetry |
| `notifications/roots/list_changed` | Removed (roots deprecated) | Paths as tool arguments |
| `resources/subscribe`, `resources/unsubscribe`, HTTP GET stream | `subscriptions/listen` | Move listeners |
| SSE resumability (`Last-Event-ID`) | Removed | Drop event stores |
| Tasks in core | `io.modelcontextprotocol/tasks` extension | Advertise under `capabilities.extensions` |
| `notifications/elicitation/complete` | Removed | Delete |

## Changed

- Every result has `resultType`: `"complete"` or `"input_required"`. Clients treat a missing field as complete.
- `tools/list` (and other lists) must come back in a deterministic order.
- List and read results may carry `ttlMs` and `cacheScope` cache hints.
- Resource not found: `-32602` (was `-32002`).
- New error codes: HeaderMismatch `-32020`, MissingRequiredClientCapability `-32021`, UnsupportedProtocolVersion
  `-32022`.
- Streamable HTTP: `MCP-Protocol-Version`, `Mcp-Method` and `Mcp-Name` headers; servers validate that they match
  the body.
- `capabilities.extensions` advertises optional extensions by prefixed identifier.
- Auth: clients validate `iss` (RFC 9207); Client ID Metadata Documents are preferred over dynamic client
  registration, which is deprecated.

## Deprecated (still on the wire for now)

Roots, sampling, protocol logging, the HTTP+SSE transport, `includeContext` values `thisServer`/`allServers`, and
dynamic client registration.

## Backward compatibility

A dual-era server answers `initialize` with legacy semantics for that stdio process or HTTP session, and serves
requests that carry modern `_meta` statelessly. A modern-only server SHOULD name its supported versions in the error
it returns to `initialize`, because legacy clients have no other diagnostic. On stdio, dual-era clients probe with
`server/discover` first and fall back on any error that is not a recognised modern error.

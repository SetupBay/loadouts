---
name: go-mcp-tool
description: Add a tool to a Go MCP server built on the official go-sdk, with typed input and output, input validation, tool errors and an in-memory client test.
---

# Add a tool to a Go MCP server

Examples: `references/server.go` and `references/server_test.go`.

1. Define `XInput` and `XOutput` structs. Every field gets a `json` tag and a `jsonschema` tag describing it in plain
   words. Optional fields use `omitempty`.
2. Write the handler with the signature
   `func(ctx context.Context, req *mcp.CallToolRequest, in XInput) (*mcp.CallToolResult, XOutput, error)`.
   Validate `in` first. Return `nil, XOutput{...}, nil` on success; the SDK fills in structured content.
   Return an error for anything the model should see as a failed call.
3. Register it in the server constructor: `mcp.AddTool(s, &mcp.Tool{Name: "x", Description: "..."}, handler)`.
   Keep the constructor separate from `main` so tests can build the server.
4. Test it through a real client over `mcp.NewInMemoryTransports()`: list tools, call it with good input, and call it
   with bad input expecting `IsError`.
5. Run `gofmt -l .`, `go vet ./...` and `go test -race ./...`.
6. Logging goes to stderr only. Check there is no `fmt.Print` in the package.

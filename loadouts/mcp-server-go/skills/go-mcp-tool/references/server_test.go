package main

import (
	"context"
	"encoding/json"
	"strings"
	"testing"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

func connect(t *testing.T) *mcp.ClientSession {
	t.Helper()
	ctx := context.Background()
	clientTransport, serverTransport := mcp.NewInMemoryTransports()
	if _, err := NewServer().Connect(ctx, serverTransport, nil); err != nil {
		t.Fatal(err)
	}
	client := mcp.NewClient(&mcp.Implementation{Name: "test-client", Version: "v0"}, nil)
	session, err := client.Connect(ctx, clientTransport, nil)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { _ = session.Close() })
	return session
}

func TestListTools(t *testing.T) {
	res, err := connect(t).ListTools(context.Background(), nil)
	if err != nil {
		t.Fatal(err)
	}
	if len(res.Tools) != 1 || res.Tools[0].Name != "lookup_term" {
		t.Fatalf("unexpected tools: %+v", res.Tools)
	}
	schema, _ := json.Marshal(res.Tools[0].InputSchema)
	if !strings.Contains(string(schema), "case-insensitive") {
		t.Fatalf("input schema lost the field description: %s", schema)
	}
}

func TestLookupTerm(t *testing.T) {
	session := connect(t)
	tests := []struct {
		name    string
		args    map[string]any
		wantErr string
		want    string
	}{
		{name: "found", args: map[string]any{"term": " Loadout "}, want: "agent instruction files"},
		{name: "unknown", args: map[string]any{"term": "widget"}, wantErr: "unknown term"},
		{name: "empty", args: map[string]any{"term": ""}, wantErr: "1-64 characters"},
		{name: "bad limit", args: map[string]any{"term": "skill", "limit": 50}, wantErr: "between 1 and 10"},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			res, err := session.CallTool(context.Background(), &mcp.CallToolParams{Name: "lookup_term", Arguments: tc.args})
			if err != nil {
				t.Fatalf("protocol error: %v", err)
			}
			text := res.Content[0].(*mcp.TextContent).Text
			if tc.wantErr != "" {
				if !res.IsError || !strings.Contains(text, tc.wantErr) {
					t.Fatalf("want tool error containing %q, got isError=%v %q", tc.wantErr, res.IsError, text)
				}
				return
			}
			if res.IsError {
				t.Fatalf("unexpected tool error: %s", text)
			}
			out, _ := json.Marshal(res.StructuredContent)
			if !strings.Contains(string(out), tc.want) {
				t.Fatalf("structured content %s does not contain %q", out, tc.want)
			}
		})
	}
}

// Command glossary is an MCP server with one read-only tool that looks up project terms.
package main

import (
	"context"
	"fmt"
	"log/slog"
	"os"
	"sort"
	"strings"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// LookupInput is the tool's input. The jsonschema tags become the schema the model reads.
type LookupInput struct {
	Term  string `json:"term" jsonschema:"the glossary term to look up, case-insensitive"`
	Limit int    `json:"limit,omitempty" jsonschema:"maximum number of related terms to return (1-10, default 3)"`
}

// LookupOutput is the tool's structured result.
type LookupOutput struct {
	Term       string   `json:"term"`
	Definition string   `json:"definition"`
	Related    []string `json:"related"`
}

var glossary = map[string]string{
	"loadout": "A set of agent instruction files, skills and MCP configs for one kind of project.",
	"skill":   "A folder with a SKILL.md that an agent loads when the task matches its description.",
	"fixture": "A small project the verifier copies a loadout into and runs commands against.",
}

func lookup(ctx context.Context, req *mcp.CallToolRequest, in LookupInput) (*mcp.CallToolResult, LookupOutput, error) {
	term := strings.ToLower(strings.TrimSpace(in.Term))
	if term == "" || len(term) > 64 {
		return nil, LookupOutput{}, fmt.Errorf("term must be 1-64 characters")
	}
	limit := in.Limit
	if limit == 0 {
		limit = 3
	}
	if limit < 1 || limit > 10 {
		return nil, LookupOutput{}, fmt.Errorf("limit must be between 1 and 10, got %d", limit)
	}
	def, ok := glossary[term]
	if !ok {
		return nil, LookupOutput{}, fmt.Errorf("unknown term %q; try one of: %s", term, strings.Join(terms(), ", "))
	}
	related := make([]string, 0, limit)
	for _, t := range terms() {
		if t != term && len(related) < limit {
			related = append(related, t)
		}
	}
	return nil, LookupOutput{Term: term, Definition: def, Related: related}, nil
}

func terms() []string {
	out := make([]string, 0, len(glossary))
	for t := range glossary {
		out = append(out, t)
	}
	sort.Strings(out)
	return out
}

// NewServer builds the server. Tests call it directly; main serves it over stdio.
func NewServer() *mcp.Server {
	s := mcp.NewServer(&mcp.Implementation{Name: "glossary", Version: "v0.1.0"}, nil)
	mcp.AddTool(s, &mcp.Tool{
		Name:        "lookup_term",
		Description: "Look up a project glossary term. Returns the definition and related terms. Read-only.",
	}, lookup)
	return s
}

func main() {
	// stdout carries the protocol; logs go to stderr.
	logger := slog.New(slog.NewTextHandler(os.Stderr, nil))
	if err := NewServer().Run(context.Background(), &mcp.StdioTransport{}); err != nil {
		logger.Error("server stopped", "err", err)
		os.Exit(1)
	}
}

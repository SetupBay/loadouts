// A stdio MCP server on the TypeScript SDK v2 that speaks protocol 2026-07-28
// and still serves 2025-era clients from the same factory.
// Before (v1): new McpServer(...) + server.connect(new StdioServerTransport())
// After  (v2): serveStdio(() => buildServer())
import type { CallToolResult, InputRequiredResult } from "@modelcontextprotocol/server";
import { acceptedContent, inputRequired, McpServer } from "@modelcontextprotocol/server";
import { serveStdio } from "@modelcontextprotocol/server/stdio";
import * as z from "zod/v4";

const GLOSSARY: Record<string, { definition: string; related: string[] }> = {
  loadout: { definition: "A bundle of agent instructions, skills and config for one kind of project.", related: ["skill", "fixture"] },
  skill: { definition: "A folder with a SKILL.md that an agent loads when the task matches.", related: ["loadout"] },
  fixture: { definition: "A small sample project the verifier runs a loadout against.", related: ["loadout"] },
};

// Notes live in the process for the demo. No state is keyed on a session:
// 2026-07-28 has no sessions, so anything a later call needs is passed back in
// the tool's own arguments (here, the note id).
const notes = new Map<string, string>([["n1", "Rotate the staging API key"], ["n2", "Book the retro"]]);

const confirmSchema = z.object({ confirm: z.boolean().meta({ title: "Delete this note?" }) });

function buildServer(): McpServer {
  const server = new McpServer(
    { name: "notes", version: "1.0.0" },
    { capabilities: { tools: {} }, instructions: "Glossary lookups and a small notes list." },
  );

  // Tools are registered in a fixed order; tools/list order must be deterministic.
  server.registerTool(
    "lookup_term",
    {
      description: "Look up a glossary term. Returns the definition and related terms. Read-only.",
      inputSchema: z.object({ term: z.string().min(1).max(64).describe("Glossary term, case-insensitive") }),
      annotations: { readOnlyHint: true },
    },
    async ({ term }): Promise<CallToolResult> => {
      const entry = GLOSSARY[term.toLowerCase()];
      if (!entry) {
        return { isError: true, content: [{ type: "text", text: `Unknown term "${term}". Known: ${Object.keys(GLOSSARY).join(", ")}` }] };
      }
      return { content: [{ type: "text", text: JSON.stringify({ term, ...entry }) }] };
    },
  );

  // v1 called ctx.mcpReq.elicitInput() here (a server-to-client request). That
  // channel is gone in 2026-07-28: return input_required and let the client
  // retry the same call with the answer (multi-round-trip requests).
  server.registerTool(
    "delete_note",
    {
      description: "Delete a note by id after the user confirms. Destructive.",
      inputSchema: z.object({ id: z.string().min(1).max(16).describe("Note id, for example n1") }),
      annotations: { destructiveHint: true },
    },
    async ({ id }, ctx): Promise<CallToolResult | InputRequiredResult> => {
      const text = notes.get(id);
      if (text === undefined) {
        return { isError: true, content: [{ type: "text", text: `No note "${id}". Ids: ${[...notes.keys()].join(", ")}` }] };
      }
      const answer = acceptedContent(ctx.mcpReq.inputResponses, "confirm", confirmSchema);
      if (answer === undefined) {
        return inputRequired({
          inputRequests: { confirm: inputRequired.elicit({ message: `Delete "${text}"?`, requestedSchema: confirmSchema }) },
        });
      }
      if (!answer.confirm) return { content: [{ type: "text", text: `Kept ${id}.` }] };
      notes.delete(id);
      return { content: [{ type: "text", text: `Deleted ${id}.` }] };
    },
  );

  return server;
}

const handle = serveStdio(buildServer);
console.error("notes MCP server on stdio (2026-07-28 and 2025-era clients)");
process.on("SIGINT", () => void handle.close());

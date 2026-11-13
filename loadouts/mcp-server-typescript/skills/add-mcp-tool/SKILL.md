---
name: add-mcp-tool
description: Design, implement and test a new tool on a TypeScript MCP server. Use when the user asks to add a capability, endpoint or action to their MCP server.
---

# Add an MCP tool

## 1. Design first (write this down in your reply)
- **Name:** verb-first `snake_case`, not clashing with existing tools (check `src/tools/`).
- **Description:** 1–3 sentences for the model — what it does, when to use it instead of the other tools, what it returns.
- **Inputs:** each field with type, constraints and description. Keep it to what the model can reasonably know.
- **Output:** the few fields the model needs, formatted as short text or compact JSON.
- **Failure cases:** list them and the message each returns.
- **Side effects:** read-only, or does it change something? Destructive tools need a confirmation input or a human decision first.

If an existing tool almost does this, propose extending it instead of adding a near-duplicate.

## 2. Implement
Create `src/tools/<name>.ts` with a `register(server)` function, following the patterns already in the repo and the SDK version installed.
The shape (adjust to the installed SDK's API):

```ts
import { z } from "zod";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

export function register(server: McpServer) {
  server.registerTool(
    "get_weather",
    {
      title: "Get weather",
      description: "Current weather for a city. Use for present conditions only; there is no forecast. Returns temperature (°C), conditions and wind.",
      inputSchema: { city: z.string().min(1).max(100).describe("City name, e.g. 'Leeds' or 'Leeds, UK'") },
      annotations: { readOnlyHint: true },
    },
    async ({ city }) => {
      const result = await lookupWeather(city);
      if (!result) {
        return { isError: true, content: [{ type: "text", text: `No city called "${city}" found. Try adding the country.` }] };
      }
      return { content: [{ type: "text", text: `${result.name}: ${result.tempC}°C, ${result.summary}, wind ${result.windKph} km/h` }] };
    },
  );
}
```

Register it in `src/index.ts`. Put API calls in `src/lib/` with timeouts.

## 3. Test
1. `npm run build` (and `npm test` if there are tests; add one for the handler logic).
2. `npx @modelcontextprotocol/inspector node dist/index.js` → Tools → list → call with valid input, then invalid input.
3. Confirm nothing is written to stdout except protocol messages.

## 4. Report
The tool signature, its description, sample output, and how to reload it in the human's client
(most clients need the MCP server restarted to see new tools).

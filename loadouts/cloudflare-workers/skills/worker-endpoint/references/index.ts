// Example Worker: bindings from env, validated input, prepared D1 statements, waitUntil for background work.
// The Env interface is what `npx wrangler types` generates for these bindings.

export interface Env {
  DB: D1Database;
  CACHE: KVNamespace;
  ALLOWED_ORIGIN: string;
}

type Note = { id: number; text: string; created_at: string };

const json = (data: unknown, status = 200, origin?: string): Response =>
  new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      ...(origin ? { "Access-Control-Allow-Origin": origin, Vary: "Origin" } : {}),
    },
  });

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") === env.ALLOWED_ORIGIN ? env.ALLOWED_ORIGIN : undefined;

    if (request.method === "GET" && url.pathname.startsWith("/notes/")) {
      const id = Number(url.pathname.slice("/notes/".length));
      if (!Number.isInteger(id) || id < 1) return json({ error: "id must be a positive integer" }, 400, origin);
      const cached = await env.CACHE.get<Note>(`note:${id}`, "json");
      if (cached) return json(cached, 200, origin);
      const note = await env.DB.prepare("SELECT id, text, created_at FROM notes WHERE id = ?").bind(id).first<Note>();
      if (!note) return json({ error: "not found" }, 404, origin);
      ctx.waitUntil(env.CACHE.put(`note:${id}`, JSON.stringify(note), { expirationTtl: 300 }));
      return json(note, 200, origin);
    }

    if (request.method === "POST" && url.pathname === "/notes") {
      let body: unknown;
      try {
        body = await request.json();
      } catch {
        return json({ error: "invalid JSON" }, 400, origin);
      }
      const text = typeof body === "object" && body !== null && "text" in body ? (body as { text: unknown }).text : undefined;
      if (typeof text !== "string" || text.length === 0 || text.length > 2000) {
        return json({ error: "text must be 1 to 2000 characters" }, 400, origin);
      }
      const row = await env.DB.prepare("INSERT INTO notes (text) VALUES (?) RETURNING id, text, created_at")
        .bind(text)
        .first<Note>();
      return json(row, 201, origin);
    }

    return json({ error: "not found" }, 404, origin);
  },
} satisfies ExportedHandler<Env>;

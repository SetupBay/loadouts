import { Agent, callable, routeAgentRequest } from "agents";

export type Env = {
  ReminderAgent: DurableObjectNamespace<ReminderAgent>;
};

type State = { pending: number };

// One instance per name (a user, a chat room): state and SQL live in that instance's Durable Object.
export class ReminderAgent extends Agent<Env, State> {
  initialState: State = { pending: 0 };

  async onStart() {
    this.sql`CREATE TABLE IF NOT EXISTS reminders (
      id TEXT PRIMARY KEY, text TEXT NOT NULL, due INTEGER NOT NULL, sent INTEGER NOT NULL DEFAULT 0)`;
  }

  // Callable from the client over the WebSocket (agent.call / useAgent). Validate everything.
  @callable()
  async addReminder(text: string, delaySeconds: number) {
    const clean = typeof text === "string" ? text.trim() : "";
    if (!clean || clean.length > 200) throw new Error("text must be 1 to 200 characters");
    if (!Number.isInteger(delaySeconds) || delaySeconds < 1 || delaySeconds > 30 * 86400) {
      throw new Error("delaySeconds must be a whole number from 1 to 2592000");
    }
    const id = crypto.randomUUID();
    const due = Date.now() + delaySeconds * 1000;
    this.sql`INSERT INTO reminders (id, text, due) VALUES (${id}, ${clean}, ${due})`;
    await this.schedule(delaySeconds, "sendReminder", { id });
    this.setState({ pending: this.state.pending + 1 });
    return { id, due };
  }

  @callable()
  async listReminders() {
    return this.sql<{ id: string; text: string; due: number }>`
      SELECT id, text, due FROM reminders WHERE sent = 0 ORDER BY due`;
  }

  // Runs from the Durable Object alarm, even if no client is connected.
  async sendReminder(payload: { id: string }) {
    const [row] = this.sql<{ text: string }>`
      UPDATE reminders SET sent = 1 WHERE id = ${payload.id} AND sent = 0 RETURNING text`;
    if (!row) return; // already sent (schedules can run more than once)
    this.setState({ pending: Math.max(0, this.state.pending - 1) });
    this.broadcast(JSON.stringify({ type: "reminder", text: row.text }));
  }
}

export default {
  async fetch(request, env) {
    // Routes /agents/reminder-agent/<name> (HTTP and WebSocket) to the right instance.
    return (await routeAgentRequest(request, env)) ?? new Response("Not found", { status: 404 });
  },
} satisfies ExportedHandler<Env>;

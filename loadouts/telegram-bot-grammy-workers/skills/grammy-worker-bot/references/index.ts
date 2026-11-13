// Telegram bot on Cloudflare Workers with grammY 1.46. One update per request, answered inside grammY's
// 10-second webhook window; anything slow goes to a Queue (see SKILL.md).
import { Bot, webhookCallback } from "grammy";
import type { UserFromGetMe } from "grammy/types";

export interface Env {
  BOT_TOKEN: string; // wrangler secret put BOT_TOKEN
  WEBHOOK_SECRET: string; // wrangler secret put WEBHOOK_SECRET; the same value goes to setWebhook as secret_token
  BOT_INFO: string; // getMe result as JSON in vars, so the bot doesn't call getMe on every request
}

type ClientOptions = NonNullable<ConstructorParameters<typeof Bot>[1]>["client"];

const PORTS = new Map([
  ["whitby", "High water 06:12 and 18:40"],
  ["dover", "High water 04:55 and 17:21"],
]);

// Plain logic, no Telegram objects: easy to test.
export function tideReply(input: string): string {
  const port = input.trim().toLowerCase();
  if (!port) return "Usage: /tide <port>, for example /tide Whitby";
  return PORTS.get(port) ?? "I don't know that port yet.";
}

export function createBot(env: Env, client?: ClientOptions): Bot {
  const bot = new Bot(env.BOT_TOKEN, { botInfo: JSON.parse(env.BOT_INFO) as UserFromGetMe, client });
  // bot.catch() only applies to long polling. With webhooks an uncaught error fails the request and Telegram resends
  // the same update, so handlers go inside an error boundary that logs and lets the request finish with 200.
  const safe = bot.errorBoundary((err) => console.error(`update ${err.ctx.update.update_id} failed:`, err.error));
  safe.command("start", (ctx) => ctx.reply("Send /tide <port> for today's high water."));
  safe.command("tide", (ctx) => ctx.reply(tideReply(ctx.match)));
  return bot;
}

export async function handle(request: Request, env: Env, client?: ClientOptions): Promise<Response> {
  const url = new URL(request.url);
  if (request.method !== "POST" || url.pathname !== "/telegram") return new Response("Not found", { status: 404 });
  // secretToken makes grammY reject requests without the matching X-Telegram-Bot-Api-Secret-Token header (401).
  return webhookCallback(createBot(env, client), "cloudflare-mod", { secretToken: env.WEBHOOK_SECRET })(request);
}

export default {
  fetch: (request, env) => handle(request, env),
} satisfies ExportedHandler<Env>;

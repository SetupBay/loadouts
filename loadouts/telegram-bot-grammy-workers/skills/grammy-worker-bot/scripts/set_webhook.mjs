#!/usr/bin/env node
// Point Telegram at the Worker, with the secret token. The human runs this after a deploy they approved.
//   BOT_TOKEN=... WEBHOOK_SECRET=... node set_webhook.mjs https://tide-bot.example.workers.dev/telegram [message,callback_query]
// Prints Telegram's answer and getWebhookInfo, never the token.
const [url, updates = "message,callback_query"] = process.argv.slice(2);
const { BOT_TOKEN: token, WEBHOOK_SECRET: secret } = process.env;
if (!url || !url.startsWith("https://")) {
  console.error("usage: node set_webhook.mjs https://<worker>/telegram [comma-separated update types]");
  process.exit(2);
}
if (!token || !secret) {
  console.error("set BOT_TOKEN and WEBHOOK_SECRET in the environment (the same secret the Worker has)");
  process.exit(2);
}
if (!/^[A-Za-z0-9_-]{1,256}$/.test(secret)) {
  console.error("WEBHOOK_SECRET must be 1-256 characters of A-Z, a-z, 0-9, _ and -");
  process.exit(2);
}
const api = (method, body) =>
  fetch(`https://api.telegram.org/bot${token}/${method}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body ?? {}),
  }).then((r) => r.json());

const set = await api("setWebhook", { url, secret_token: secret, allowed_updates: updates.split(",") });
console.log("setWebhook:", set.ok ? set.description : `failed: ${set.description}`);
const info = await api("getWebhookInfo");
const { url: u, pending_update_count, last_error_message, allowed_updates } = info.result ?? {};
console.log(JSON.stringify({ url: u, pending_update_count, last_error_message, allowed_updates }, null, 2));
process.exit(set.ok ? 0 : 1);

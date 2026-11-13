---
name: grammy-worker-bot
description: Build or change a Telegram bot that runs on Cloudflare Workers with grammY 1.46, including the webhook secret, bot info, error boundary, tests with a fake Bot API, and setting the webhook after a deploy. Use for any command, handler, config or webhook work on a grammY Worker bot.
---

# grammY bot on Cloudflare Workers

## Shape of the project
- `src/index.ts`: see `references/index.ts`. It exports `handle(request, env, client?)` so tests can pass a fake
  `fetch`, and a default `{ fetch }` handler for the Worker.
- `wrangler.jsonc`: see `references/wrangler.jsonc`. `BOT_INFO` in `vars`, nothing secret there.
- `.dev.vars` (git ignored) holds `BOT_TOKEN` and `WEBHOOK_SECRET` for `wrangler dev`.

## Adding a command
1. Write the logic as a plain function first (`tideReply(input)` in the reference) and test it directly.
2. Register it on the error boundary, not on `bot`: `safe.command("tide", (ctx) => ctx.reply(tideReply(ctx.match)))`.
3. If it needs anything slow, reply first ("Working on it") and send the job to a Queue binding. The consumer sends the
   result with `bot.api.sendMessage(chatId, ...)`.
4. Add a test that posts real update JSON (copy one from getUpdates on a test bot, then strip personal data) through
   `handle()` with a fake client and asserts the Bot API calls.

## Prove it
```sh
npx tsc --noEmit
node --test test/
node .agents/skills/grammy-worker-bot/scripts/bot_check.mjs .
```
The tests must show a 401 for a missing or wrong secret, one `sendMessage` call and no `getMe` for a good update, and
a 200 when a handler throws. `bot_check.mjs` must report `0 to fix`.

## Going live (only when the human asks)
1. `npx wrangler secret put BOT_TOKEN` and `npx wrangler secret put WEBHOOK_SECRET` (the human types the values).
2. `npx wrangler deploy`.
3. The human runs `node .agents/skills/grammy-worker-bot/scripts/set_webhook.mjs https://<worker>/telegram` with
   `BOT_TOKEN` and `WEBHOOK_SECRET` in their environment. It calls setWebhook with `secret_token` and
   `allowed_updates`, then prints getWebhookInfo (pending count and last error) without the token.
4. Check `last_error_message` is empty after a test message. A growing `pending_update_count` means the Worker isn't
   answering with 200.

## Don't
- Don't log `ctx.update` wholesale; it has users' names and messages.
- Don't create the Bot in module scope with env values; build it per request from `env`.
- Don't paste a real token into a test or fixture, even a test bot's.

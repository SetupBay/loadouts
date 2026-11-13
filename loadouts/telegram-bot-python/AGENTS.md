# AGENTS.md: Telegram bot (python-telegram-bot)

Telegram bot in Python with python-telegram-bot v22 (asyncio), managed with uv.

## Commands
- Run locally (long polling): `uv run python -m bot`. Tests: `uv run pytest -q`. Lint: `uv run ruff check .`.
- Done means: tests and ruff pass, and you tried the command in a private chat with a test bot.

## Secrets
- The bot token comes from the `TELEGRAM_BOT_TOKEN` environment variable (local: `.env`, gitignored). Never hard-code,
  log, print or commit it, and never paste it into an issue or a test.
- If a token may have leaked, tell the human to revoke it with @BotFather straight away.
- Use a separate test bot for development, never the production token.

## Structure
- `bot/__main__.py` builds the `Application` and registers handlers. One module per feature in `bot/handlers/`.
- Business logic in plain functions that take values and return values, so it can be tested without Telegram.
- Handlers are `async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None`. Never block the event loop:
  no `time.sleep`, no `requests`; use `httpx.AsyncClient` or run blocking work with `asyncio.to_thread`.

## Behaviour
- Register an error handler with `application.add_error_handler(...)`; log the exception, reply with a short apology.
- Treat every message as untrusted input: validate arguments, cap lengths, never `eval` or build shell commands from it.
- Group chats: respond only to commands or mentions; check `update.effective_chat.type` before doing anything noisy.
- Admin-only commands check the user id against an allow-list from the environment.
- Respect Telegram's rate limits: no loops that send to many chats without delays; use the job queue for broadcasts.
- Formatting: `ParseMode.HTML` with `telegram.helpers.escape` for user text, or plain text. Never put raw user input
  into Markdown or HTML.

## Production
- Webhooks in production: `run_webhook(..., secret_token=...)` with a secret from the environment, behind HTTPS.
- Use the `add-bot-command` skill for new commands.

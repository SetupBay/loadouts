# AGENTS.md: Discord bot (Python, discord.py 2)

## Layout
```
bot.py            creates the Bot, loads cogs in setup_hook, reads the token from the environment
cogs/<name>.py    one feature per cog: app commands plus an async setup(bot) function
tests/            pytest for command logic and the command payloads, no network
```
Run with `uv run python bot.py`. Tests: `uv run pytest`. Lint: `uv run ruff check` and `uv run ruff format --check`.

## Commands
- Slash commands (`app_commands`), not prefix commands that need the privileged message content intent.
- Every command and option has a description (`description=` and `@app_commands.describe`). Names are lowercase,
  1-32 characters.
- Constrain options in the schema: `app_commands.Range[int, 1, 20]`, `Range[str, 1, 200]`, `Choice` lists. Discord
  enforces these before your code runs.
- Keep logic in plain functions that take plain values, so tests do not need Discord objects. New commands: use the
  `discord-py-command` skill.

## Interactions
- Respond within 3 seconds. For slow work call `await interaction.response.defer()` first, then
  `await interaction.followup.send(...)`.
- Private replies: `ephemeral=True`. Errors go to a command `.error` handler (or `tree.on_error`): log the exception,
  reply with a short ephemeral message, never a traceback.
- Moderation commands set `@app_commands.default_permissions(...)` and re-check permissions in code.
- Cooldowns on costly commands: `@app_commands.checks.cooldown(rate, per, key=...)`.

## Syncing
- Do not call `tree.sync()` on every start; it is rate limited. Sync by hand, to a dev guild while developing
  (instant), and globally only for a release.
- After changing a command's name, options or descriptions, remind the user to sync.

## Token and intents
- `DISCORD_TOKEN` comes from the environment or a git-ignored `.env`. Never print, log or commit it. If it leaks, the
  user must reset it in the Developer Portal.
- `discord.Intents.default()` is enough for slash commands. `members`, `presences` and `message_content` are
  privileged; ask before enabling them.

## Dependencies
- `uv add "discord.py==2.7.1"` and commit `uv.lock`. Ask before adding anything else. Never pass user input to a
  shell, `eval` or a SQL string.

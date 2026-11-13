---
name: discord-py-command
description: Add a slash command to a discord.py 2 bot as a cog, with described and range-limited options, a cooldown, an error handler and offline tests of the logic and the command payload.
---

# Add a discord.py slash command

Examples: `references/dice.py` (cog), `references/bot.py` (entry point) and `references/test_dice.py` (tests).

1. Put the logic in a plain function that takes plain values and returns plain values (`roll(count, sides, rng)`).
   Inject randomness, clocks and HTTP clients so tests can control them.
2. Create or extend a cog in `cogs/<feature>.py`:
   - `@app_commands.command(name=..., description=...)`
   - `@app_commands.describe(...)` for every option
   - `app_commands.Range[...]` or `Choice` for limits
   - a cooldown for anything costly, and `@app_commands.default_permissions` for moderation
3. Respond within 3 seconds; defer first if the work may be slow.
4. Add a `.error` handler: cooldowns get a friendly ephemeral message; anything else is logged and gets
   "Something went wrong."
5. Export `async def setup(bot)` and add the module to the extensions list in `bot.py`.
6. Tests, with no network: the logic function (including bad input), and the payload Discord will receive:
   `bot.add_cog(...)`, then `c.to_dict(bot.tree)` for each command, checking names, descriptions and limits.
7. Run `uv run pytest`, `uv run ruff check` and `uv run ruff format --check`. Remind the user to sync commands.

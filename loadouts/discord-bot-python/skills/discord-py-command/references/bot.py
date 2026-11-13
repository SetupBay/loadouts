"""Entry point: minimal intents, cogs loaded in setup_hook, token from the environment, no sync on start."""

import asyncio
import logging
import os

import discord
from discord.ext import commands

EXTENSIONS = ["cogs.dice"]


class Bot(commands.Bot):
    def __init__(self) -> None:
        # Slash commands need no privileged intents. Do not enable message_content or members unless required.
        super().__init__(command_prefix=commands.when_mentioned, intents=discord.Intents.default())

    async def setup_hook(self) -> None:
        for ext in EXTENSIONS:
            await self.load_extension(ext)
        guild_id = os.environ.get("DISCORD_DEV_GUILD_ID")
        if os.environ.get("SYNC_COMMANDS") == "1" and guild_id:
            # Sync by hand, to one dev guild: instant, and avoids the global sync rate limit.
            guild = discord.Object(id=int(guild_id))
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logging.info("synced %d commands to guild %s", len(synced), guild_id)


async def main() -> None:
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise SystemExit("DISCORD_TOKEN is not set (put it in .env, never in code)")
    discord.utils.setup_logging()
    async with Bot() as bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())

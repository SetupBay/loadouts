"""Dice cog: one slash command with validated options, a cooldown and logic that can be tested offline."""

import logging
import random

import discord
from discord import app_commands
from discord.ext import commands

log = logging.getLogger(__name__)

MAX_DICE = 20


def roll(count: int, sides: int, rng: random.Random) -> list[int]:
    """Pure logic, no Discord objects: easy to test."""
    if not 1 <= count <= MAX_DICE:
        raise ValueError(f"count must be 1-{MAX_DICE}")
    if not 2 <= sides <= 1000:
        raise ValueError("sides must be 2-1000")
    return [rng.randint(1, sides) for _ in range(count)]


def format_roll(results: list[int], sides: int) -> str:
    total = sum(results)
    shown = ", ".join(map(str, results)) if len(results) <= 10 else f"{len(results)} dice"
    return f"Rolled {len(results)}d{sides}: {shown} (total {total})"


class Dice(commands.Cog):
    def __init__(self, bot: commands.Bot, rng: random.Random | None = None) -> None:
        self.bot = bot
        self.rng = rng or random.Random()

    @app_commands.command(name="roll", description="Roll dice, for example 3 six-sided dice")
    @app_commands.describe(count="How many dice (1-20)", sides="Sides per die (2-1000)")
    @app_commands.checks.cooldown(1, 3.0, key=lambda i: i.user.id)
    async def roll_command(
        self,
        interaction: discord.Interaction,
        count: app_commands.Range[int, 1, MAX_DICE] = 1,
        sides: app_commands.Range[int, 2, 1000] = 6,
    ) -> None:
        results = roll(count, sides, self.rng)
        await interaction.response.send_message(format_roll(results, sides))

    @roll_command.error
    async def roll_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            message = f"Slow down: try again in {error.retry_after:.0f}s."
        else:
            log.exception("roll failed", exc_info=error)
            message = "Something went wrong."
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Dice(bot))

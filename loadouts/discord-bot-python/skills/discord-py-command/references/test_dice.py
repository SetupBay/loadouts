import asyncio
import random

import discord
import pytest
from discord.ext import commands

from cogs.dice import Dice, format_roll, roll


def test_roll_is_deterministic_with_a_seeded_rng():
    assert roll(3, 6, random.Random(42)) == roll(3, 6, random.Random(42))
    assert all(1 <= r <= 6 for r in roll(20, 6, random.Random(1)))


@pytest.mark.parametrize(("count", "sides"), [(0, 6), (21, 6), (1, 1), (1, 1001)])
def test_roll_rejects_out_of_range(count, sides):
    with pytest.raises(ValueError):
        roll(count, sides, random.Random(0))


def test_format_roll_summarises_many_dice():
    assert format_roll([1, 2, 3], 6) == "Rolled 3d6: 1, 2, 3 (total 6)"
    assert format_roll([1] * 12, 4) == "Rolled 12d4: 12 dice (total 12)"


def test_command_payload_registers_offline():
    async def build():
        bot = commands.Bot(command_prefix=commands.when_mentioned, intents=discord.Intents.default())
        await bot.add_cog(Dice(bot))
        return [c.to_dict(bot.tree) for c in bot.tree.get_commands()]

    (payload,) = asyncio.run(build())
    assert payload["name"] == "roll"
    options = {o["name"]: o for o in payload["options"]}
    assert options["count"]["description"] == "How many dice (1-20)"
    assert (options["count"]["min_value"], options["count"]["max_value"]) == (1, 20)
    assert options["sides"]["max_value"] == 1000
    assert not options["count"]["required"]

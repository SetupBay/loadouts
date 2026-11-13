"""Example command: /split <amount> <people> splits a bill. Logic is a plain function; the handler is a thin wrapper."""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

USAGE = "Usage: /split <amount> <people>, for example /split 42.50 3"


def parse_split(args: list[str]) -> str:
    if len(args) != 2:
        raise ValueError(USAGE)
    try:
        amount = Decimal(args[0].replace("£", ""))
        people = int(args[1])
    except (InvalidOperation, ValueError):
        raise ValueError(USAGE) from None
    if amount <= 0 or amount > Decimal("100000"):
        raise ValueError("Amount must be between 0 and 100,000.")
    if not 1 <= people <= 100:
        raise ValueError("People must be between 1 and 100.")
    share = (amount / people).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"£{amount:.2f} split {people} ways is £{share} each."


async def split_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    try:
        text = parse_split(context.args or [])
    except ValueError as err:
        text = str(err)
    await update.message.reply_text(text)


def register(application: Application) -> None:
    application.add_handler(CommandHandler("split", split_command))

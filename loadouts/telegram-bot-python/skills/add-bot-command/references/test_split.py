import pytest
from telegram.ext import Application, CommandHandler

from bot.handlers.split import USAGE, parse_split, register


def test_even_split():
    assert parse_split(["42.50", "3"]) == "£42.50 split 3 ways is £14.17 each."


def test_pound_sign_allowed():
    assert parse_split(["£10", "4"]) == "£10.00 split 4 ways is £2.50 each."


@pytest.mark.parametrize("args", [[], ["10"], ["ten", "2"], ["10", "two"], ["10", "2", "3"]])
def test_bad_arguments_show_usage(args):
    with pytest.raises(ValueError, match="Usage"):
        parse_split(args)


@pytest.mark.parametrize("args, message", [(["0", "2"], "Amount"), (["10", "0"], "People"), (["10", "1000"], "People")])
def test_out_of_range(args, message):
    with pytest.raises(ValueError, match=message):
        parse_split(args)


def test_usage_mentions_command():
    assert "/split" in USAGE


def test_handler_is_registered_without_network():
    app = Application.builder().token("123456:TEST-TOKEN-NOT-REAL").build()
    register(app)
    commands = [c for h in app.handlers[0] if isinstance(h, CommandHandler) for c in h.commands]
    assert "split" in commands

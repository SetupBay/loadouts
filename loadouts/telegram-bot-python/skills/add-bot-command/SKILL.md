---
name: add-bot-command
description: Add a python-telegram-bot command with logic in a testable plain function, validated arguments, escaped output and a unit test. Use when adding or changing a bot command.
---

# Add a bot command

1. Write the logic as a plain function first (no Telegram types), like `parse_split` in `references/split.py`.
   It validates input and raises `ValueError` with a message the user can read.
2. Write the handler: read `context.args`, call the function, reply with the result. Catch `ValueError` and reply with
   its message plus usage. Escape any user text with `telegram.helpers.escape` if you reply in HTML.
3. Register it in `bot/__main__.py`: `application.add_handler(CommandHandler("split", split_command))`.
4. Add the command to the BotFather command list text in the README, so the human can update it.
5. Tests like `references/test_split.py`: the plain function (valid, invalid, edge cases) and that the application
   registers the handler. No network, no token.
6. Run `uv run pytest -q` and `uv run ruff check .`, then try it with the test bot.

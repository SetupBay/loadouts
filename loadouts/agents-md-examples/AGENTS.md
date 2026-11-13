# AGENTS.md: keeping this repository's AGENTS.md right

This repository's `AGENTS.md` files are instructions for every coding agent that works here. Treat them like code:
they must be correct, short and checked.

## When you change an AGENTS.md
- Use the `agents-md-writer` skill. It has seven worked examples and a lint script.
- Every command in it must exist and work. Run it before you write it down.
- Keep the five parts: what the project is, Commands, Layout, Conventions and Never, Done means.
- Keep each file under 150 lines and the root-to-folder chain under 32 KiB.
- A CLAUDE.md must import `AGENTS.md` with a line `@AGENTS.md`; never put different rules in the two files.

## When the code changes
If you rename a script, move a folder or change the test runner, update the AGENTS.md that mentions it in the same
change, and run the lint again.

## Never
- Write a command you have not run, or one copied from another project
- Put rules in CLAUDE.md, GEMINI.md or Cursor rules that contradict AGENTS.md

## Done means
The lint prints `0 error(s)`, and every warning left is explained in your report.

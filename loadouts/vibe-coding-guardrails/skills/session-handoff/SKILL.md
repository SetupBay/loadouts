---
name: session-handoff
description: Write or update NOTES.md so the next session or another agent can continue the work. Use at the end of a long session, before context runs out, or when the user says they are stopping for now.
---

# Session handoff

Update (or create) `NOTES.md` at the repository root. Replace the "Current state" section; append to "Log".
Keep the whole file short enough to read in a minute. Do not include secrets, tokens or personal data.

```markdown
# Notes

## Current state (updated <YYYY-MM-DD>)
- Working on: <the feature/bug, one line>
- Done this session: <bullets, with file paths>
- In progress: <what is half-finished and where; say if the build is currently broken>
- Next steps: <ordered list, small enough to start immediately>
- Decisions: <choices made and why, so they are not relitigated>
- Gotchas: <surprising things learned: env quirks, flaky tests, API oddities>

## How to run
<the commands that actually work right now: install, dev, test, build>

## Log
- <YYYY-MM-DD>: <one line per session>
```

Then:
1. Run `git status` and mention any uncommitted changes. Suggest a commit message, but do not commit unless asked.
2. Tell the human, in two or three lines, where things stand and what the next session should start with.

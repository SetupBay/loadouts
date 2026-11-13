---
name: resume-from-handoff
description: Pick up work from HANDOFF.md at the start of a session. Checks the handoff is current, re-runs its verify commands and confirms the next step before changing anything.
---

# Resume from a handoff

1. Read `HANDOFF.md` in full before opening other files.
2. Check it is current: `python3 .agents/skills/write-handoff/scripts/check_handoff.py HANDOFF.md` (or the same script
   under `.claude/skills/`). If it reports "stale", run `git log --oneline <recorded commit>..HEAD` and read what
   changed before trusting the "Current state" section.
3. Re-run the "Verify with" commands. Compare the result with "Failing or open". Note any difference.
4. Check the "Tools and MCP servers needed" are available in this agent. If one is missing, say so; do not guess.
5. Reply to the user in two or three sentences: the goal, what you found when you re-ran the checks, and the next step
   you propose. Wait for a yes if anything differs from the handoff.
6. As you work, keep `HANDOFF.md` updated at natural stopping points, using the `write-handoff` skill.

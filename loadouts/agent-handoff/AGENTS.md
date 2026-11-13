# AGENTS.md: hand off work without compaction

Long sessions end in one of three ways: the context fills and gets compacted, you `/clear`, or the work moves to another
agent or person. Compaction keeps what a summariser thought mattered. A handoff file keeps what the next session needs.

## When to write a handoff
- Before `/clear`, `/compact` or ending a long session with work unfinished.
- Before switching agents (for example Claude Code to Codex or Antigravity) or handing to a teammate.
- When the context is clearly getting long: answers slow down, you re-read files you already read, or you lose track
  of earlier decisions. Do not wait for automatic compaction.
- Use the `write-handoff` skill. It writes `HANDOFF.md` at the repo root and checks it.

## When to read one
- At the start of every session, if `HANDOFF.md` exists, use the `resume-from-handoff` skill before doing anything
  else. Confirm the goal and next step with the user in one or two sentences.

## Rules for the file
- Facts, not narrative: goal, current state, files touched, decisions with reasons, what still fails (exact error),
  the next step, and the commands that prove it works.
- Record the commit (`git rev-parse --short HEAD`) and branch. A handoff for a different commit is stale until checked.
- Short: under 120 lines. Link to files and line numbers instead of pasting code.
- No secrets, tokens or personal data. It may be committed or shared.
- One owner per open task. If something is unverified, say so; do not round "probably works" up to "done".
- Delete or archive the file (`git rm HANDOFF.md` or move it to `docs/handoffs/`) when the work is finished.

## MCP servers and tools
- Note which MCP servers and CLIs the work depended on. A new agent may not have them configured.

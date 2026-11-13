---
name: unity-plugin-setup
description: Install and check Unity's official agent plugin for Claude Code or Codex, and prepare the project (git, ignore file, Unity CLI). Use when the Unity skills are missing or before the first agent session in a Unity project.
---

# Set up the Unity agent plugin

1. **Project checks.** Unity 6+ (`ProjectSettings/ProjectVersion.txt`). The project is a git repository with a Unity
   `.gitignore` that excludes `Library/`, `Temp/`, `Logs/`, `obj/`, `UserSettings/`. If not, propose one and ask.
2. **Install** (the human runs these; they change the agent's own configuration):
   - Claude Code, inside a session: `/plugin marketplace add Unity-Technologies/unity-agent-plugin`, then
     `/plugin install unity@unity-agent-plugin`. From a terminal: `claude plugin marketplace add …` and
     `claude plugin install unity@unity-agent-plugin`, then `/reload-plugins`.
   - Codex: `codex plugin marketplace add Unity-Technologies/unity-agent-plugin`, then `codex plugin add unity@unity-agent-plugin`.
3. **Check.** Claude Code: typing `/unity:` lists the skills. Codex: `codex plugin list` shows `unity`.
4. **Unity CLI.** Many skills work best with the Unity CLI talking to the open Editor. When a task needs it, the plugin
   offers to install it; tell the human before accepting, because it adds a package to the project. Commit first.
5. **First task.** Start with something small and reviewable (a settings screen, an input mapping) and review the diff
   and the scene changes in the Editor before larger work.

Source: github.com/Unity-Technologies/unity-agent-plugin (README, checked 16 October 2026).

---
name: add-slash-command
description: Add a new slash command to a discord.js v14 bot, register it and document it. Use when the user asks for a new bot command, e.g. "add a /poll command".
---

# Add a slash command

1. **Clarify in one line** if needed: command name, options (name, type, required?), who can use it, public or private reply.
   Otherwise choose sensible defaults and state them.
2. **Check the name is free:** look in `src/commands/` and in the `data.setName(...)` calls.
3. **Create `src/commands/<name>.ts`** following the command file shape in AGENTS.md:
   - `SlashCommandBuilder` with name, description, typed options with limits.
   - Moderation or admin commands: `.setDefaultMemberPermissions(PermissionFlagsBits.<Perm>)` and `.setContexts(InteractionContextType.Guild)`
     so they cannot run in DMs.
   - `execute`: validate, `deferReply()` if anything is slow, do the work, reply.
   - Handle the expected failures (missing permission, bad input, external API down) with a friendly ephemeral message.
4. **Check the loader** in `src/index.ts` picks up new files automatically. If commands are listed by hand, add it there and in
   `deploy-commands.ts`.
5. **Type-check:** `npm run build` or `npx tsc --noEmit`.
6. **Register:** tell the human to run `npm run deploy` (guild registration is instant). Only run it yourself if they ask and
   `.env` is already set up — it uses the bot token.
7. **Document:** add the command to the commands table in `README.md` (name, options, who can use it).
8. **Report:** the file created, the command signature (`/poll question:<text> duration:<minutes>`), and how to try it.

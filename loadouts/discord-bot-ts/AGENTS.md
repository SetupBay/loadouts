# AGENTS.md: Discord bot (TypeScript, discord.js v14)

## Layout
```
src/
  index.ts            creates the Client, loads commands and events, logs in
  deploy-commands.ts  registers slash commands with Discord (run by hand, not on every start)
  commands/<name>.ts  one slash command per file: exports `data` (SlashCommandBuilder) and `execute(interaction)`
  events/<name>.ts    one gateway event per file: exports `name`, `once?`, `execute(...)`
  lib/                shared helpers (embeds, db, permissions)
```
Run with `npm run dev` (tsx watch) locally. `npm run deploy` runs `deploy-commands.ts`.

## Command file shape
Each file in `src/commands/` exports `data` and `execute`, nothing else:

```ts
import { SlashCommandBuilder, type ChatInputCommandInteraction } from "discord.js";

export const data = new SlashCommandBuilder()
  .setName("roll")                       // lowercase, 1–32 chars, no spaces
  .setDescription("Roll a dice")         // required, 1–100 chars
  .addIntegerOption((o) => o.setName("sides").setDescription("Number of sides").setMinValue(2).setMaxValue(1000));

export async function execute(interaction: ChatInputCommandInteraction) {
  const sides = interaction.options.getInteger("sides") ?? 6;
  const result = 1 + Math.floor(Math.random() * sides);
  await interaction.reply({ content: `🎲 ${result} (d${sides})` });
}
```

## Token and secrets
- `DISCORD_TOKEN`, `DISCORD_CLIENT_ID`, `DISCORD_GUILD_ID` come from `.env` (git-ignored). `.env.example` lists them with dummy values.
- Never print the token, commit it, or paste it into an embed or error message. If it leaks, the human must reset it in the
  Developer Portal → Bot → Reset Token. Discord also auto-revokes tokens it finds in public repos.

## Intents
- Request the minimum: `GatewayIntentBits.Guilds` covers slash commands.
- `GuildMembers`, `GuildPresences` and `MessageContent` are **privileged**: they must be switched on in the Developer
  Portal and are reviewed once a bot is in 100+ servers. Prefer slash commands over reading message content.

## Interactions
- Discord gives you **3 seconds** to respond. If work might take longer (API calls, database, AI), call
  `await interaction.deferReply()` first, then `await interaction.editReply(...)`.
- Private replies: `interaction.reply({ content, flags: MessageFlags.Ephemeral })`. (`ephemeral: true` is deprecated.)
- Every `execute` is wrapped by the loader in try/catch. On error: log it, then reply or follow up with a short
  ephemeral "Something went wrong" — never the stack trace.
- Check permissions for moderation commands with `.setDefaultMemberPermissions(...)` on the builder *and* re-check in code.
- Validate options: string lengths, number ranges (`.setMinValue/.setMaxValue`), and never pass user text into shell commands or eval.

## Registering commands
- During development register to one guild (`Routes.applicationGuildCommands(clientId, guildId)`) — updates are instant.
- Global registration (`Routes.applicationCommands(clientId)`) is for release. Do not register on every bot start; there are rate limits.
- After changing a command's `data`, remind the human to run `npm run deploy`.

## Style
- TypeScript strict, ES modules, `async/await`. No `any` on interaction types: use `ChatInputCommandInteraction`.
- Keep command files small; move logic into `lib/` when two commands share it.
- Rate-limit costly commands per user (a simple in-memory cooldown map is fine to start).

## Before you say "done"
`npm run build` (tsc) passes, the new command is in `commands/`, and you have told the human whether to re-run deploy.

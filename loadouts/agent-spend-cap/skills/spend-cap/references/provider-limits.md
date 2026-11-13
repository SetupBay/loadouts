# Provider-side spend limits

The guard is a soft cap in front of headless runs. These are the limits that hold even when something bypasses it.
Check each against the provider's current docs before relying on it.

## Claude Code

- Per run: `claude -p ... --max-budget-usd <amount>` (print mode only). With `--output-format json` the result
  includes `total_cost_usd`, a client-side estimate.
- Claude Console (API key): set workspace spend limits on the "Claude Code" workspace. Usage and cost reporting is in
  the Console.
- Pro and Max with usage credits: set a monthly spend limit under Settings > Usage on claude.ai. `/usage` shows spend
  against it.
- Team and Enterprise: admins set spend limits for the organisation, groups or individual members.
- Amazon Bedrock, Google Cloud or Microsoft Foundry: use that cloud's budget controls.

Source: https://code.claude.com/docs/en/costs and https://code.claude.com/docs/en/headless

## Codex

- `codex exec --json` emits `turn.completed` events with `usage` (`input_tokens`, `cached_input_tokens`,
  `output_tokens`, `reasoning_output_tokens`). There is no money figure and no budget flag.
- Cap spend through your OpenAI plan or API project settings, and check which of them your account actually enforces.

Source: https://developers.openai.com/codex/noninteractive and the Codex SDK event types
(https://github.com/openai/codex/blob/main/sdk/typescript/src/events.ts)

## Antigravity CLI

- `agy -p ... --output-format json` returns `usage` (`input_tokens`, `output_tokens`, `thinking_tokens`,
  `cache_read_tokens`, `total_tokens`). There is no money figure and no budget flag. `--print-timeout` bounds time,
  not tokens.
- `useG1Credits` (default `false`) lets the CLI spend personal AI credits once plan quotas are exhausted. Keep it
  `false`. `/credits` shows the remaining credits and `/usage` the model quota.

Source: https://antigravity.google/docs/cli/headless and https://antigravity.google/docs/cli/reference

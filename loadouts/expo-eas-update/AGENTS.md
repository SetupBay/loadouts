# AGENTS.md: Expo app shipped with EAS Update

An Expo SDK 58 app (React Native 0.88) built with EAS Build and updated over the air with EAS Update. Check
`package.json` for exact versions, and add packages with `npx expo install` so versions match the SDK.

## Commands
- Typecheck: `npx tsc --noEmit`.
- Bundle check: `npx expo export --platform ios --platform android --output-dir dist`.
- Update config check: `node .agents/skills/eas-update-release/scripts/ota_check.mjs config`.
- OTA safety: `node .agents/skills/eas-update-release/scripts/ota_check.mjs compare` (against the fingerprint
  recorded when the current store build was cut).

## Rules
- Use the `eas-update-release` skill before any change is published as an update, and after adding or upgrading
  a package or editing app.json, app.config or eas.json.
- `runtimeVersion` uses the fingerprint policy. If `compare` reports a native change, the change needs a new
  build: say so, do not publish an update.
- Agents may publish to the `preview` channel through CI. Production updates, rollouts and rollbacks are run by
  a person.
- Never run `eas update --auto`, `--force-end-active-rollout`, `eas update:rollback` or `eas channel:*`.
- Never edit or regenerate the committed build fingerprint to make a check pass. It is recorded when a build is cut.
- `EXPO_TOKEN` and other secrets live in CI secrets or EAS environment variables, never in the repository.
- Code that depends on a new native module checks it exists before calling it, so an older build degrades
  instead of crashing.

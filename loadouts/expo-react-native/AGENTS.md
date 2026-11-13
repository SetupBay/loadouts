# AGENTS.md: Expo / React Native app

React Native app on Expo with Expo Router and TypeScript. Check the Expo SDK version in `package.json` before using an API.

## Commands
- Start: `npx expo start`. Lint: `npx expo lint`. Types: `npx tsc --noEmit`. Tests: the project's test script.
- Health check after dependency changes: `npx expo-doctor`.
- Add a package: `npx expo install <package>` so the version matches the SDK. Never plain `npm install` for native packages.
- Done means: lint, type-check and tests pass, and expo-doctor reports no problems you introduced.

## Project rules
- Routes are files in `app/` (Expo Router). Layouts in `_layout.tsx`; do not hand-roll a navigator alongside the router.
- Native config lives in `app.json` or `app.config.ts` and config plugins. If `ios/` and `android/` are generated
  (Continuous Native Generation, listed in `.gitignore`), never edit them; change config and run `npx expo prebuild --clean`.
- Packages with native code need a development build, not Expo Go. Say so when you add one.
- `EXPO_PUBLIC_` variables are compiled into the app and visible to anyone. Never put secrets in them; secrets stay on a server.
- Use platform-specific files (`.ios.tsx`, `.android.tsx`) or `Platform.select` only when behaviour really differs.
- Lists use `FlatList` or `FlashList`, never `map` inside a `ScrollView` for long data.

## Releases
- Never run `eas build --profile production`, `eas submit` or `eas update` on a production channel without the human
  asking for it in this session. Preview builds and updates to a preview channel are fine when asked.
- Bumping the Expo SDK is its own task: follow the upgrade guide, run `npx expo install --fix`, then expo-doctor.

## Expo MCP and skills
- The Expo MCP server (`expo` in the MCP config) gives live docs, EAS build logs and, with a running dev server,
  simulator screenshots. Prefer it over guessing APIs from memory. It signs in with your Expo account (OAuth).
- Use the `expo-change` skill for any feature or fix.

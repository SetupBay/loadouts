---
name: expo-change
description: Make a feature or fix in an Expo app with SDK-matched packages, Expo Router conventions, a check on a simulator or device and no production releases. Use for any change to an Expo / React Native app.
---

# Expo change

1. Read `package.json` (Expo SDK), `app.json` or `app.config.ts`, and the routes in `app/` that the change touches.
2. Look up the API in the current docs (Expo MCP `search_documentation` / `read_documentation`, or docs.expo.dev) for
   this SDK version. Do not rely on memory for package APIs; they change between SDKs.
3. New packages: `npx expo install <package>`. If it has native code, note that a development build is needed.
4. Make the change in TypeScript, following the router layout. Keep secrets out of `EXPO_PUBLIC_` variables.
5. Run `npx expo lint`, `npx tsc --noEmit`, the tests and, after dependency changes, `npx expo-doctor`.
6. Check it runs: with the dev server up, open the screen on a simulator or device. With Expo MCP local capabilities,
   take a screenshot and look at it; otherwise ask the human to check and describe what to look for.
7. Report: files changed, packages added (and whether a new dev build is needed), check results, screenshot if taken.

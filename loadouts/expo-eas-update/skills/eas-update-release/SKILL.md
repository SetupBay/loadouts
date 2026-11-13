---
name: eas-update-release
description: Decide whether an Expo change can ship as an EAS Update or needs a new store build, check the update config, and prepare a staged rollout. Use before publishing with eas update, after adding or upgrading a package, or when editing app.json, app.config or eas.json.
---

# Shipping with EAS Update

An EAS Update replaces the JavaScript and assets inside a build. It cannot change native code. If an update
calls a native module the build does not contain, it crashes on users' phones, and `expo-updates` falls back
to the previous update only if it notices. This skill keeps that from happening.

## 1. Config once: fingerprint runtime version and one channel per profile

```bash
node .agents/skills/eas-update-release/scripts/ota_check.mjs config
```

It reads the resolved app config (`npx expo config --type public`) and checks:

- `runtimeVersion` is `{ "policy": "fingerprint" }` (top level or per platform). The fingerprint changes
  whenever anything that affects the native layer changes. A manual string or `appVersion` policy only works
  if someone remembers to bump it, so the script notes it.
- `updates.url` is `https://u.expo.dev/<projectId>` and matches `extra.eas.projectId`.
- `eas.json` parses with Expo's own validator (`@expo/eas-json`), and every non-development build profile has
  its own `channel`, including one called `production`.

Start from `references/app.json` and `references/eas.json`.

## 2. Every change: is it OTA-safe?

When a store build is cut, record its native fingerprint and commit the file:

```bash
node .agents/skills/eas-update-release/scripts/ota_check.mjs record      # writes .eas/build-fingerprint.json
```

Before any update, compare:

```bash
node .agents/skills/eas-update-release/scripts/ota_check.mjs compare
```

- `OTA-safe` (exit 0): only JavaScript, assets or non-native config changed. An update can carry it.
- `needs a new build` (exit 1): it lists what changed, for example `added: node_modules/expo-camera/package.json`
  or `changed: expoConfig`. Do not publish an update. Say a new build is needed and why.

Typical "needs a build" changes: adding or upgrading any package with native code (`npx expo install` of an
`expo-*` module), a new config plugin, permissions, icons and splash, bundle identifiers, an SDK upgrade.
A version bump alone does not change the fingerprint.

With an Expo account the same check is `eas fingerprint:compare --build-id <id>`. The script is for CI and
for machines without a token.

## 3. Publishing: preview by the pipeline, production by a person

- Preview: CI publishes to the `preview` channel when `compare` passes. See
  `references/eas-update-preview.yml`. `--environment` is required for SDK 55 and later.
- Production, done by a person after testing on a preview build, as a staged rollout:

  ```bash
  eas update:republish --branch preview --destination-channel production --rollout-percentage 10 -m "..."
  eas update:edit                      # raise the percentage once crash-free rates hold
  eas update:revert-update-rollout     # or back out
  ```

- One rollout per branch and runtime at a time. Never pass `--force-end-active-rollout` to get past one.
- Roll back with `eas update:rollback`. A person runs it; it affects every user on that runtime.

## What the agent does not do

- No `eas update` to the `production` channel or branch, no `--auto` (it publishes to a branch named after
  the git branch), no `update:rollback`, `channel:edit` or `channel:rollout`.
- No publishing when `compare` says a build is needed, and no editing the baseline file to make it pass.
- No `EXPO_TOKEN` in files, logs or commands. It lives in CI secrets only.

## Before you call it done

1. `npx tsc --noEmit` is clean.
2. `npx expo export --platform ios --platform android --output-dir dist` succeeds (the same bundle step an
   update runs).
3. `ota_check.mjs compare` result is stated in the summary, with the changed sources if a build is needed.

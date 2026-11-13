---
name: eas-maestro-e2e
description: Set up or change Maestro end-to-end tests on EAS Workflows for an Expo app - fingerprint, get-build, repack or build, then the maestro job - and check the workflow, build profile and flows before anything spends build minutes. Use for any work on .eas/workflows, the e2e build profile or maestro/ flows.
---

# Maestro on EAS Workflows

## The pipeline (see `references/e2e.yml`)
1. `fingerprint` hashes the native parts of the project (CNG projects only; committed android/ios folders break it).
2. `get-build` looks for an existing e2e build with that fingerprint.
3. Found: `repack` puts the new JavaScript into it (minutes, no native build). Not found: `build` with the e2e profile.
4. `maestro` installs the result on an iOS Simulator or Android Emulator and runs the flows. `after:` waits for
   whichever of repack or build ran; `build_id` takes the one that produced an output.

## Setting it up
1. Add the `e2e` profile from `references/eas-e2e-profile.json` to `eas.json` (simulator iOS build, APK Android
   build, same `environment` as the fingerprint job).
2. Copy `references/e2e.yml` to `.eas/workflows/e2e.yml`. Change the branch filter and tags to fit the project.
3. Put flows in `maestro/flows/`. Tag the quick ones `smoke`; the workflow runs only those on pull requests.
4. Credentials: the human creates EAS environment variables such as `MAESTRO_TEST_PASSWORD` with secret visibility
   in the preview environment. Flows use `${MAESTRO_TEST_PASSWORD}`.

## Changing a flow
- Run it locally first (`maestro test maestro/flows/<flow>.yaml`) on a simulator or emulator with a dev build.
- Start from a clean state (`launchApp: { clearState: true }`), select by `id:` (the component's `testID`), end with
  an `assertVisible` on something only the success state shows.

## Check before pushing
```sh
uv run .agents/skills/eas-maestro-e2e/scripts/workflow_check.py .
```
It must report `0 to fix`. It catches missing `build_id` or `flow_path`, flow paths that don't exist, Android jobs
without a nested-virtualization worker, profiles that build an AAB or a device IPA, flows with the wrong `appId`,
literal secrets in `env`, `retries` above 2, and a fingerprint environment that doesn't match the build profile.

## Running it
Only when the human asks: they push the branch or run `eas workflow:run .eas/workflows/e2e.yml`. Read the result
in the Expo dashboard; screenshots and recordings are in the "Maestro Test Results" artifact.

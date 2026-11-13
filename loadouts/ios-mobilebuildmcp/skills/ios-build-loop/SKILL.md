---
name: ios-build-loop
description: Build, test, run and look at an iOS or macOS change through MobileBuildMCP, then fix what the build log or the screen shows. Use for every change to a Swift app.
---

# iOS build loop

1. Session setup (once): discover projects and schemes, list simulators, and set session defaults for project or
   workspace, scheme and simulator. Prefer a recent iPhone simulator that is already booted.
2. Baseline: build and run the tests before changing anything, so later failures are known to be yours.
3. Make the change. Keep it small; one screen or one behaviour.
4. Build for the simulator. Read errors and new warnings from the structured build output and fix them before going on.
5. Run the tests for the scheme. A failing test you did not touch means stop and report.
6. Launch the app on the simulator, go to the changed screen and take a screenshot or read the UI hierarchy.
   Compare with what was asked; if it is wrong, go back to step 3.
7. Capture logs if the change involves runtime behaviour; look for new errors.
8. Report: what changed, build and test results, and the screenshot.

On a device: device tools need code signing set up in Xcode by the human. Do not change signing to make it work.

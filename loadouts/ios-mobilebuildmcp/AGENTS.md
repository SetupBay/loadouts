# AGENTS.md: iOS and macOS app with MobileBuildMCP

Swift app built with Xcode. The agent builds, runs and tests through MobileBuildMCP (formerly XcodeBuildMCP), not by
guessing `xcodebuild` flags.

## Tools
- MCP server `mobilebuildmcp` (pinned in the MCP config). On first use in a session, list projects and schemes, and set
  the session defaults (project or workspace, scheme, simulator) once instead of passing them on every call.
- Telemetry is off in the MCP config (`MOBILEBUILDMCP_SENTRY_DISABLED`). Keep it that way unless the human changes it.
- If the server is unavailable, fall back to `xcodebuild -scheme <scheme> -destination 'platform=iOS Simulator,name=<device>' build test`.

## Done means
- The app builds for the simulator with no new warnings, the tests for the scheme pass, and you launched the app and
  looked at the screen you changed (screenshot or UI hierarchy through the MCP server).

## Swift rules
- Swift concurrency: UI work on `@MainActor`; no `DispatchQueue.main.async` in new code. Respect strict concurrency
  checking if the project enables it; do not silence warnings with `@unchecked Sendable` or `nonisolated(unsafe)`
  without explaining why it is safe.
- SwiftUI: small views, state owned in one place (`@State`, `@Observable` models), no business logic in `body`.
- No force unwraps (`!`) or `try!` on data from outside the app. Errors are typed and shown to the user where it matters.
- Tests with Swift Testing (`@Test`, `#expect`) for new code, unless the project only uses XCTest.

## Never
- Never edit `project.pbxproj` by hand when the change can be made through a tool, and never reorder or reformat it.
  If you must add a file, prefer a folder the project already syncs or ask the human.
- Never change signing settings, bundle identifiers, entitlements or provisioning without the human asking.
- Never upload to TestFlight or the App Store.

Use the `ios-build-loop` skill for every change.

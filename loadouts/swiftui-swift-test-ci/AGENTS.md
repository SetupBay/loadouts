# AGENTS.md: SwiftUI app with a tested Swift package core

An iOS and macOS app in SwiftUI. Screens are thin views over `@Observable` view models that live in a local Swift
package (`Packages/`), built in the Swift 6 language mode and tested with Swift Testing. Check `Package.swift` for
tools version and platforms before using an API.

## Commands (run in the package folder)
- Lint: `swift format lint --strict --recursive Sources Tests Package.swift`. Fix: `swift format --in-place --recursive Sources Tests`.
- Build and test: `swift build --build-tests` then `swift test --parallel`. This works on Linux and macOS.
- Views (macOS only): `xcodebuild -scheme <Package> -destination 'generic/platform=iOS Simulator' build`.
- Done means: lint clean, `swift test` green with a test for the behaviour you changed, and the summary says
  whether the views were compiled.

## Rules
- Use the `swiftui-testable-feature` skill when adding a screen or changing view logic.
- View models are `@MainActor @Observable final class` with `private(set)` state and no SwiftUI import.
  Logic lives there, not in `body`.
- Side effects (network, disk, clock) go through `Sendable` protocols injected in `init`. Tests use actor fakes.
- New tests use Swift Testing (`@Test`, `#expect`), with `arguments:` for input tables.
- Fix strict concurrency errors properly. Never add `@unchecked Sendable`, `nonisolated(unsafe)` or
  `@preconcurrency` to silence them.
- No force unwraps or `try!` outside tests. No new package dependencies without saying so.
- Do not change signing, entitlements, bundle identifiers or the Xcode project's build settings unless asked.

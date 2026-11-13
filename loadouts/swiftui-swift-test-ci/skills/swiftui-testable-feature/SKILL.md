---
name: swiftui-testable-feature
description: Build a SwiftUI feature with its state and logic in a Swift package view model that swift test covers on Linux and macOS, with a thin view on top. Use when adding a screen, changing view logic, or writing Swift tests.
---

# SwiftUI feature with a testable core

SwiftUI views are hard to test and only build on Apple platforms. So the view stays thin, and everything worth
testing lives in an `@Observable` view model inside a Swift package that builds and tests anywhere, including
a cheap Linux CI runner.

## Layout

```
Packages/NotesCore/
  Package.swift                      swift-tools-version 6.2, Swift 6 language mode
  Sources/NotesCore/Note.swift       value types + the client protocol (Sendable)
  Sources/NotesCore/NotesModel.swift @MainActor @Observable view model, no SwiftUI import
  Sources/NotesCore/NotesView.swift  the view, wrapped in #if canImport(SwiftUI)
  Tests/NotesCoreTests/...           Swift Testing (@Suite, @Test, #expect)
```

The app target (Xcode project) depends on the package and only creates the model with the real client.

## Rules for the view model

- `@MainActor @Observable final class`, with `private(set)` state. The view reads it and calls methods.
- State is an enum (`idle`, `loading`, `loaded`, `failed(message)`), not several booleans that can disagree.
- Every side effect goes through a `Sendable` protocol passed into `init` (network, disk, clock). Time comes
  from an injected `now` closure, so tests are deterministic.
- Derived values (sorting, filtering, validation) are computed properties or methods on the model, not code
  in `body`.
- Errors become a user-facing message in state. Never swallow them into an empty list.
- No `import SwiftUI`, `UIKit` or `AppKit` in the model file.

## Rules for the view

- Wrap the file in `#if canImport(SwiftUI)` so the package still builds on Linux.
- Own the model with `@State`, pass it down as a plain property, bind with `$model.field`.
- Load in `.task { await model.load() }`, refresh with `.refreshable`.
- No business logic in the view: if you want to test it, move it into the model.

## Tests

- Swift Testing, not XCTest, for new tests: `@Suite`, `@Test("sentence")`, `#expect`, and
  `#expect(throws:)`. Use `arguments:` for tables of inputs instead of copy-pasted tests.
- Mark the suite `@MainActor` to call the model directly.
- Fakes are `actor`s that implement the client protocol and record calls. No mocking frameworks.
- Each behaviour has a test: happy path, each error, edge input (blank, too long, whitespace), and that
  invalid input never reaches the client.

## Commands (from the package folder)

```bash
swift format lint --strict --recursive Sources Tests Package.swift   # config: references/swift-format.json as .swift-format
swift build --build-tests
swift test --parallel
```

On a Mac, also build for the simulator so the views compile:
`xcodebuild -scheme NotesCore -destination 'generic/platform=iOS Simulator' build`.
CI runs both (see `references/swift-ci.yml`): Linux in the `swift:6.4.1-noble` container, macOS with Xcode 26.6.

## Done means

- Lint is clean and `swift test` passes, with a new or changed `@Test` for the behaviour you touched.
- Strict concurrency errors are fixed, not silenced: no `@unchecked Sendable`, `nonisolated(unsafe)` or
  `@preconcurrency` added to get a build through.
- The summary says whether the views were built on macOS or only the core was tested on Linux.

## References

`references/Package.swift`, `references/Note.swift`, `references/NotesModel.swift`,
`references/NotesView.swift`, `references/NotesModelTests.swift` (six tests, nine cases),
`references/swift-format.json`, `references/swift-ci.yml`.

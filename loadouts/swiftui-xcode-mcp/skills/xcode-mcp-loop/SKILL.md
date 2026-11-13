---
name: xcode-mcp-loop
description: Change SwiftUI app code with Xcode's own MCP tools (xcrun mcpbridge, Xcode 26.3+) - build, read the log, render previews and look at them, run tests - in a tight loop. Use for any SwiftUI view, model or app change when Xcode is open on the project.
---

# Build, look, test with Xcode MCP

## 0. Connect
Call `XcodeListWindows`. Pick the entry whose workspace path is this project and keep its `tabIdentifier`. No entry,
or an error: ask the human to open the project in Xcode, check "Allow external agents to use Xcode tools" in
Settings > Intelligence, and accept the connection alert. See `references/tools.md`.

## 1. Before editing
- Run `python3 .agents/skills/xcode-mcp-loop/scripts/preview_check.py . --targets` and note the previews for the
  files you'll touch. Fix any `fix` lines in those files as part of your change.
- If you'll use an API you haven't used in this project, `DocumentationSearch` for it and check availability against
  the deployment target.

## 2. Edit, then build
1. Make one coherent change.
2. `BuildProject` with the `tabIdentifier`.
3. If it fails, `GetBuildLog` with severity `error` (or `XcodeListNavigatorIssues`), fix, and build again. Warnings
   you introduced count as errors for this loop.

## 3. Look at it
For each view you changed, `RenderPreview` with `sourceFilePath` (project-relative) and
`previewDefinitionIndexInFile` from the targets list. Open the PNG it returns and check text, spacing, truncation,
empty and error states, and large Dynamic Type if there's a preview for it. If a view has no preview, add one with
fixture data first: `#Preview("Empty") { ... }`, using `@Previewable @State` for bindings.

## 4. Test
`GetTestList`, then `RunSomeTests` for the tests that cover what you changed. Before you finish, `RunAllTests`.
Report the counts, and any test you couldn't make pass, as they are.

## 5. Report
Say which previews you rendered and what they showed, the build result and the test counts. If Xcode wasn't
reachable, say so plainly and list what you couldn't check.

## Don't
- Don't switch scheme or run destination, or change signing or build settings, to get a build through.
- Don't use `ExecuteSnippet` on code that reads files, the keychain or the network.
- Don't call previews done from the source alone; render them.

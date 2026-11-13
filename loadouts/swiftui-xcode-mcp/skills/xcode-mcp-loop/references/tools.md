# Xcode MCP tools used by this loadout

Xcode 26.3 and later ship an MCP server reached through `xcrun mcpbridge`. Xcode must be running with the project open,
and "Allow external agents to use Xcode tools" must be on in Xcode > Settings > Intelligence. Xcode shows an alert
when an agent connects; the human may have to click Allow.

| Tool | What it's for | Notes |
|---|---|---|
| XcodeListWindows | Find the `tabIdentifier` for this project | Call first; most tools need the identifier |
| BuildProject | Build the active scheme and wait | Doesn't change the scheme or destination |
| GetBuildLog | Read the latest build log | Filter by severity (error, warning), regex or file glob |
| XcodeListNavigatorIssues | Issues currently in the Issue Navigator | Same filters as GetBuildLog |
| XcodeRefreshCodeIssuesInFile | Re-check one file without a full build | Quick feedback while editing |
| GetTestList, RunSomeTests, RunAllTests | Tests from the active test plan | RunSomeTests takes targetName and testIdentifier from GetTestList |
| RenderPreview | Snapshot one SwiftUI preview to a PNG | sourceFilePath is project-relative; previewDefinitionIndexInFile is zero-based |
| DocumentationSearch | Apple docs and WWDC transcripts | Use before adopting an API you aren't sure about |
| ExecuteSnippet | Run a Swift snippet | Pure logic only, never anything that touches user data |
| XcodeRead, XcodeUpdate, XcodeWrite, XcodeGrep, XcodeGlob, XcodeLS | Files through Xcode | Your own file tools are fine for reads and edits |
| XcodeMakeDir, XcodeRM, XcodeMV | Change the file tree | Only when the human asked |

## Setting it up (the human does this once)
- Claude Code: `claude mcp add --transport stdio xcode -- xcrun mcpbridge`
- Codex: `codex mcp add xcode -- xcrun mcpbridge`
- Cursor: add the server in MCP settings with the command `xcrun mcpbridge`, or use the MCP config that comes with this loadout
- Check it with `claude mcp list` or `codex mcp list`, then ask the agent to call XcodeListWindows.

## Finding RenderPreview arguments
`preview_check.py <project dir> --targets` prints one `target <path> <index> <name>` line per preview. The path is
relative to the folder you pass, so pass the folder that contains the `.xcodeproj`.

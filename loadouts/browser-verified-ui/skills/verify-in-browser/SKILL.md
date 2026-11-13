---
name: verify-in-browser
description: Load the changed UI in a real browser through the Playwright MCP server, exercise it, check console and network errors, and capture screenshots at two widths. Use after any UI change and before reporting it done.
---

# Verify in the browser

1. **Server.** Start the dev server if it is not running (the project's dev command, in the background) and wait until
   the URL responds. Note the port.
2. **Ignore output.** Make sure `.playwright-mcp/` is in `.gitignore`; add it if not.
3. **Navigate** to the page you changed with the browser navigate tool.
4. **Snapshot.** Take an accessibility snapshot. Check the new or changed text, labels, roles and links are present.
5. **Exercise** the change the way a user would: click, type, submit, open and close. Include one error path
   (empty form, invalid input) when there is one.
6. **Errors.** Read console messages and network requests. Any error or failed request caused by the change is a failure:
   fix it and start again from step 3.
7. **Screenshots** at 390×844 and 1280×800 (resize the browser between shots). Name them `<page>-<width>.png`.
8. **Report**: URL checked, what you exercised, console and network result, screenshot paths. Close the browser.

If the Playwright tools are missing, tell the human the `playwright` MCP server is not connected and how to enable it
(`/mcp`); do not claim the UI was verified.

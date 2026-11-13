---
name: write-e2e-test
description: Write or repair a Playwright end-to-end test with role-based locators, web-first assertions and no fixed waits, then lint it and run it. Use for new user flows and for failing or flaky tests.
---

# Write or repair an end-to-end test

Example: `references/todo.spec.ts`.

## New test
1. Write the flow as steps a user takes and what they should see. One behaviour per test.
2. Open the page and find each element the way a user would: `page.getByRole("button", { name: "Add" })`.
   If you cannot find a good role or label, ask whether the app should have one before reaching for a test id.
3. Assert with web-first assertions after every meaningful step (`toBeVisible`, `toHaveText`, `toHaveCount`,
   `toHaveURL`).
4. Set up state inside the test or a fixture. Do not depend on another test having run.
5. Lint: `node scripts/lint_specs.mjs tests`. Fix every finding.
6. Run it three times in a row (`npx playwright test <file> --repeat-each 3`). Flaky means wrong, not unlucky.

## Failing or flaky test
1. Run it once with tracing: `npx playwright test <file> --trace on`, then open the trace.
2. Decide: is the app wrong, or the test? Write down which and why.
3. App wrong: stop and report the regression with the trace path. Do not edit the test.
4. Test wrong: fix the locator or the setup. Never add sleeps, never loosen assertions, never add `force: true`.
5. Lint and run three times as above.

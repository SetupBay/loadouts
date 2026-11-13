# AGENTS.md: Playwright end-to-end tests

End-to-end tests with Playwright Test (`@playwright/test`). These rules apply when you write tests by hand and when
you use Playwright's own test agents (planner, generator, healer from `npx playwright init-agents`).

## Commands
- Run: `npx playwright test`. One file: `npx playwright test tests/todo.spec.ts`. List without running:
  `npx playwright test --list`.
- Debug a failure: `npx playwright show-trace test-results/<test>/trace.zip`. Do not guess from the error alone.
- Before finishing, run the `write-e2e-test` skill's linter (`scripts/lint_specs.mjs` in the skill folder) over the
  test folder. It must report no findings.

## Writing tests
- Locate by what the user sees: `getByRole` with a name first, then `getByLabel`, `getByPlaceholder`, `getByText`.
  `getByTestId` when there is nothing better. No CSS chains, XPath or `nth-child`.
- Web-first assertions only: `await expect(locator).toBeVisible()`, `toHaveText`, `toHaveCount`, `toHaveURL`.
  Never `expect(await locator.isVisible()).toBe(true)`: it does not retry.
- No fixed waits: no `page.waitForTimeout`, no `waitForLoadState("networkidle")`. Wait for the thing you need.
- No `force: true` on clicks. If an element is covered, that is a bug or a wrong locator.
- Each test sets up its own state and runs alone and in any order. Share setup with fixtures or `beforeEach`, and
  authentication with a setup project and `storageState`.
- Never commit `test.only`. Use `test.skip` with a reason, or `test.fixme` and an issue link.
- Test data and accounts are test-only. Never use production credentials; read secrets from the environment.

## Healing failing tests
- First decide whether the test or the app is wrong. Read the trace. If the app regressed, report it; do not change
  the test to match a bug.
- Never make a test pass by deleting assertions, loosening them to `toBeTruthy`, adding timeouts or retries, or
  skipping it without saying so.
- Locator changed because the UI changed on purpose: update the locator to a role-based one and say what changed.

## Configuration
- `retries` only in CI (`process.env.CI ? 2 : 0`), with `trace: "on-first-retry"`.
- `webServer` starts the app; do not assume a server is already running.
- Ask before adding browsers, projects or dependencies. Pin `@playwright/test` to an exact version.

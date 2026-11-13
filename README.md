# SetupBay

Ready-made setups for AI coding agents. Each loadout is a small bundle of the files an agent reads when it starts work: an `AGENTS.md` with the rules for one kind of project, adapters for `CLAUDE.md` and `GEMINI.md`, Cursor rules, skills, hooks and MCP configs where they help.

This repo holds the loadouts themselves. The website at **[setupbay.com](https://setupbay.com)** has search, per-agent install steps, ready-made zips and the security notes for each one.

Works with Claude Code, Codex CLI, Cursor, Gemini CLI, Antigravity CLI and GitHub Copilot.

## Using a loadout

**Copy the files.** Every folder under [`loadouts/`](loadouts/) is one loadout. Copy what you need into your project root. A few things to know:

- `AGENTS.md` goes in the project root. If you already have one, merge the two rather than overwriting yours.
- `CLAUDE.md` and `GEMINI.md` just point Claude Code and Gemini CLI at `AGENTS.md`.
- Skills live under `skills/<name>/` here. Claude Code reads them from `.claude/skills/<name>/`, and most other agents from `.agents/skills/<name>/`.
- `listing.yaml` describes the loadout: what each file is for, the tools it needs, what the security scan found, and the sources it draws on. You don't need to copy it.

If you'd rather not move files around by hand, each loadout's page on the site has a zip already laid out for your agent.

**Use the MCP server.** Add SetupBay to your agent as a remote MCP server and ask it to find and install a loadout for your project:

```
https://setupbay.com/mcp
```

For Claude Code, for example:

```
claude mcp add --transport http setupbay https://setupbay.com/mcp
```

The agent can search loadouts, read every file and get the install steps for itself. It should show you what it's about to write before it writes anything.

**Claude Code plugins.** Loadouts with skills or MCP servers are also available as plugins:

```
/plugin marketplace add https://setupbay.com/marketplace.json
```

Plugins can't carry project rules, so `AGENTS.md` and `CLAUDE.md` still come from the folder here or the loadout's page.

## Suggesting a loadout

Got a setup that works well for you, or spotted something wrong in one of these? Send it through the [submit page](https://setupbay.com/submit/). Credit goes to whoever the ideas came from, and every loadout lists its sources in `listing.yaml`.

## Loadouts

89 loadouts, grouped by what they're for.

### Web apps

| Loadout | What it does |
| --- | --- |
| [Astro static site](loadouts/astro-static-site/) | Astro conventions for fast, zero-JS-by-default sites with content collections, plus a skill for deploying to Cloudflare Pages with headers and redirects. [Page](https://setupbay.com/loadouts/astro-static-site/) |
| [Browser-verified UI changes](loadouts/browser-verified-ui/) | Make the agent load every UI change in a real browser via Playwright MCP, exercise it, fail on console or network errors and attach screenshots at two widths. [Page](https://setupbay.com/loadouts/browser-verified-ui/) |
| [Cloudflare Agents SDK, wired right before deploy](loadouts/cloudflare-agents-sdk/) | Stateful agents on Workers with the agents package (SQL, state, schedules, @callable) and a check that every Agent class is bound, on SQLite, with nodejs_compat. [Page](https://setupbay.com/loadouts/cloudflare-agents-sdk/) |
| [Cloudflare Workers rules](loadouts/cloudflare-workers/) | Workers rules for agents: bindings from env, wrangler types, prepared D1 queries, waitUntil, secrets via wrangler secret, no deploys or --remote writes unasked. [Page](https://setupbay.com/loadouts/cloudflare-workers/) |
| [Django 6 guard for removed APIs and django-upgrade](loadouts/django-6-upgrade-guard/) | Stop agents writing url(), ugettext, is_ajax(), index_together and CheckConstraint(check=) into Django 6.1 projects, then run django-upgrade and Django's own checks. [Page](https://setupbay.com/loadouts/django-6-upgrade-guard/) |
| [Django app rules](loadouts/django-app/) | Django rules and a safe-migration skill: migrations checked in CI, two-step destructive changes, N+1 caught with query-count tests, settings from the environment. [Page](https://setupbay.com/loadouts/django-app/) |
| [Django REST Framework API rules](loadouts/django-rest-api/) | DRF rules for agents: explicit serializer fields, querysets scoped to the user, owner set on the server, pagination, and six tests for every endpoint. [Page](https://setupbay.com/loadouts/django-rest-api/) |
| [Electron desktop app rules](loadouts/electron-app/) | Electron rules for agents: sandboxed renderers, narrow contextBridge APIs, sender-checked IPC, deny-by-default windows, CSP and fuses, with a static security check. [Page](https://setupbay.com/loadouts/electron-app/) |
| [Electron end-to-end tests with Playwright](loadouts/electron-playwright-e2e/) | Playwright tests that drive the real Electron app: secure webPreferences, no Node in the renderer, IPC round trips, input validation and blocked navigation. [Page](https://setupbay.com/loadouts/electron-playwright-e2e/) |
| [Expo and React Native with Expo MCP](loadouts/expo-react-native/) | Expo rules for agents plus Expo's official MCP server: npx expo install, Expo Router, no secrets in EXPO_PUBLIC_, no production EAS releases, check on a simulator. [Page](https://setupbay.com/loadouts/expo-react-native/) |
| [Expo EAS Update without shipping native changes over the air](loadouts/expo-eas-update/) | Checks whether an Expo change can ship as an EAS Update or needs a new build, using the native fingerprint; preview by CI, production rollouts by a person. [Page](https://setupbay.com/loadouts/expo-eas-update/) |
| [FastAPI guard against Pydantic v1 code](loadouts/fastapi-pydantic-v2-guard/) | Stop agents writing class Config, orm_mode, @validator, .dict() and pydantic.v1 into FastAPI apps on Pydantic v2, and catch Optional fields that became required. [Page](https://setupbay.com/loadouts/fastapi-pydantic-v2-guard/) |
| [FastAPI service rules](loadouts/fastapi-service/) | Rules and an endpoint skill for FastAPI with uv and Pydantic v2: Annotated dependencies, typed responses, async only when awaited, lifespan, routes with tests. [Page](https://setupbay.com/loadouts/fastapi-service/) |
| [FastAPI with async SQLAlchemy 2.1 and Alembic](loadouts/fastapi-async-sqlalchemy/) | FastAPI on async SQLAlchemy 2.1: per-request AsyncSession, lazy="raise" with eager loads, async Alembic with alembic check, and tests that count queries. [Page](https://setupbay.com/loadouts/fastapi-async-sqlalchemy/) |
| [Go service rules](loadouts/go-service/) | Go rules for agents: wrapped errors with errors.Is, context first, owned goroutines, 1.22+ routing, timeouts, and gofmt, vet and go test -race as the gate. [Page](https://setupbay.com/loadouts/go-service/) |
| [iOS builds with MobileBuildMCP (XcodeBuildMCP)](loadouts/ios-mobilebuildmcp/) | Let the agent build, test, run and screenshot iOS and macOS apps through MobileBuildMCP, pinned with telemetry off, with Swift concurrency and pbxproj rules. [Page](https://setupbay.com/loadouts/ios-mobilebuildmcp/) |
| [Maestro end-to-end tests on EAS Workflows](loadouts/expo-maestro-eas-workflows/) | Run Maestro flows on EAS Workflows with fingerprint, get-build and repack, so pull requests skip native builds, plus a check of profiles, workers and flows. [Page](https://setupbay.com/loadouts/expo-maestro-eas-workflows/) |
| [Maestro UI flows for iOS and Android agents](loadouts/maestro-mobile-flows/) | Maestro MCP and CLI for coding agents: inspect the screen, try commands inline, save flows with ids and assertions, lint them, then run the smoke set. [Page](https://setupbay.com/loadouts/maestro-mobile-flows/) |
| [Next.js + Supabase SaaS](loadouts/nextjs-supabase-saas/) | Rules, an RLS audit skill and a read-only Supabase MCP config for vibe-coding a Next.js App Router SaaS without leaking your database. [Page](https://setupbay.com/loadouts/nextjs-supabase-saas/) |
| [Next.js 16 for agents: bundled docs and dev-server MCP](loadouts/nextjs-16-agent-loop/) | Agents read the docs shipped with the installed Next.js, check code with the dev server's MCP tools, keep the managed AGENTS.md block intact and leave agent feedback off. [Page](https://setupbay.com/loadouts/nextjs-16-agent-loop/) |
| [Page speed with Chrome DevTools MCP, measured not guessed](loadouts/chrome-devtools-web-perf/) | Chrome DevTools MCP pinned with a throwaway profile and telemetry off, plus a trace, fix, re-trace loop that compares medians with Core Web Vitals thresholds. [Page](https://setupbay.com/loadouts/chrome-devtools-web-perf/) |
| [Playwright end-to-end tests agents don't make flaky](loadouts/playwright-e2e-tests/) | Rules for agents writing and healing Playwright tests, including Playwright's test agents: role locators, web-first assertions, no sleeps, never weaken a test to pass. [Page](https://setupbay.com/loadouts/playwright-e2e-tests/) |
| [Rails app rules](loadouts/rails-app/) | Rails 8 rules for agents: reversible migrations with real constraints, params.expect, N+1 checks with assert_queries_count, and rubocop and brakeman as the gate. [Page](https://setupbay.com/loadouts/rails-app/) |
| [Rails request specs with RSpec and FactoryBot](loadouts/rails-rspec/) | RSpec request specs for Rails 8.1 JSON endpoints: happy path, 422 errors, missing params, owner scoping and mass assignment, with FactoryBot and rubocop-rspec. [Page](https://setupbay.com/loadouts/rails-rspec/) |
| [SQLAlchemy 2 guard against 1.x and legacy Query code](loadouts/sqlalchemy-2-style-guard/) | Stop agents writing engine.execute, select([...]), row["name"] and session.query into SQLAlchemy 2 projects, and catch writes that are never committed. [Page](https://setupbay.com/loadouts/sqlalchemy-2-style-guard/) |
| [Starlight docs on Astro 7 with checked links](loadouts/astro-starlight-docs/) | Agent rules for Starlight 0.42 docs sites on Astro 7: front matter that search and llms.txt can use, links the validator checks, and the 0.39 sidebar change. [Page](https://setupbay.com/loadouts/astro-starlight-docs/) |
| [Supabase with a safe agent](loadouts/supabase-agent-safety/) | Supabase MCP scoped to one dev project, read-only, database and docs tools only; every change as a reviewed migration with RLS, policy and expand-contract rules. [Page](https://setupbay.com/loadouts/supabase-agent-safety/) |
| [SwiftUI with a Swift package core and swift test in CI](loadouts/swiftui-swift-test-ci/) | SwiftUI screens as thin views over @Observable view models in a Swift package, with Swift Testing tests run by swift test on Linux and macOS CI. [Page](https://setupbay.com/loadouts/swiftui-swift-test-ci/) |
| [SwiftUI with Xcode's MCP tools (build, preview, test)](loadouts/swiftui-xcode-mcp/) | Use Xcode 26.3+'s MCP server (xcrun mcpbridge) to build, read the log, render and look at SwiftUI previews, and run tests after every change. [Page](https://setupbay.com/loadouts/swiftui-xcode-mcp/) |
| [Tauri 2 guard for Tauri 1 imports, config and Rust APIs](loadouts/tauri-2-api-guard/) | Stop agents writing @tauri-apps/api/tauri, appWindow, the allowlist, get_window and emit_all into Tauri 2 apps, and catch the snake_case invoke arguments Tauri 2 rejects. [Page](https://setupbay.com/loadouts/tauri-2-api-guard/) |

### Workflow

| Loadout | What it does |
| --- | --- |
| [AI code review rules](loadouts/ai-code-review-rules/) | Review-only rule files for Claude Code Review, Cursor Bugbot and Copilot, built from one list: severity, a nit cap, what to skip and what to always check. [Page](https://setupbay.com/loadouts/ai-code-review-rules/) |
| [Claude Code hooks guard rails](loadouts/claude-code-hooks-guardrails/) | Fail-closed PreToolUse, post-edit and Stop hooks that block force-pushes, .env reads and wild deletes, check each edit and run tests before done. [Page](https://setupbay.com/loadouts/claude-code-hooks-guardrails/) |
| [Definition of done for agents, with proof](loadouts/definition-of-done-proof/) | Make "done" mean the feature works, a test shows it, and no test was weakened, with a git-diff check for changed assertions, skips and deleted tests. [Page](https://setupbay.com/loadouts/definition-of-done-proof/) |
| [Guarded Ralph loop](loadouts/ralph-loop-guarded/) | Run an agent in a Ralph-style loop with guard rails: a fresh process per pass, state in files, iteration and no-progress limits, and a check it cannot fake. [Page](https://setupbay.com/loadouts/ralph-loop-guarded/) |
| [Handoff without compaction](loadouts/agent-handoff/) | Write HANDOFF.md before you clear context or switch agents: goal, decisions, exact failing test, next step, commit. A checker flags stale or incomplete handoffs. [Page](https://setupbay.com/loadouts/agent-handoff/) |
| [Headless agents in CI](loadouts/headless-agents-ci/) | Rules and a GitHub Actions template for unattended claude -p or codex exec: bare mode, read-only, a spend cap, pinned versions, PR text as untrusted data. [Page](https://setupbay.com/loadouts/headless-agents-ci/) |
| [Markdown docs with markdownlint and offline link checks](loadouts/docs-markdown-checks/) | Agent-written READMEs and docs checked offline: markdownlint-cli2, relative links and #anchors resolve, and every npm run command in the docs exists. [Page](https://setupbay.com/loadouts/docs-markdown-checks/) |
| [Overnight agent runs with budgets and a morning report](loadouts/overnight-agent-runs/) | Queue coding tasks to run unattended, each with a finish-line check, its own worktree and branch, a dollar cap inside a nightly total, and safe retry settings. [Page](https://setupbay.com/loadouts/overnight-agent-runs/) |
| [Parallel agents in git worktrees](loadouts/parallel-agents-worktrees/) | Rules and two skills for running several coding agents at once, one task per git worktree: isolation, ports, dependencies, rebasing and clean-up. [Page](https://setupbay.com/loadouts/parallel-agents-worktrees/) |
| [PR hygiene for agents](loadouts/pr-hygiene-for-agents/) | Commit and PR rules for coding agents: small PRs, a four-part body, screenshots with gh --attach and a leak check for session links and secrets before pushing. [Page](https://setupbay.com/loadouts/pr-hygiene-for-agents/) |
| [Rust crate rules](loadouts/rust-crate/) | Rust rules for agents: typed errors instead of unwrap, clippy -D warnings, fmt and tests as the done-gate, no unsafe without a SAFETY note, no surprise MSRV bumps. [Page](https://setupbay.com/loadouts/rust-crate/) |
| [Second-opinion review from another model](loadouts/second-opinion-review/) | Before calling work done, the agent gets a read-only review of its diff from a different model, checks each finding and stops after two rounds. [Page](https://setupbay.com/loadouts/second-opinion-review/) |
| [Spec first, then tickets](loadouts/spec-first-tickets/) | Lightweight spec-driven flow: a SPEC.md with testable acceptance criteria, small tickets, test-first builds in parallel waves and a review against the spec. [Page](https://setupbay.com/loadouts/spec-first-tickets/) |
| [Vibe-coding guard rails](loadouts/vibe-coding-guardrails/) | A stack-agnostic working style for coding agents — plan first, small diffs, never delete tests to go green — plus handoff notes and up-to-date docs via MCP. [Page](https://setupbay.com/loadouts/vibe-coding-guardrails/) |
| [Writing rules that avoid AI-sounding prose](loadouts/no-ai-voice-writing/) | Rules and a linter that stop agents writing 'seamlessly empowers', 'not just X, it's Y', fake proof and em-dash runs into your docs, PRs and release notes. [Page](https://setupbay.com/loadouts/no-ai-voice-writing/) |

### Agent files and agents

| Loadout | What it does |
| --- | --- |
| [AGENTS.md examples for seven kinds of repository](loadouts/agents-md-examples/) | Seven worked AGENTS.md examples (web app, Python library, monorepo, Go CLI, Godot game, OpenTofu) and a lint that checks commands exist, sizes, and CLAUDE.md shadowing. [Page](https://setupbay.com/loadouts/agents-md-examples/) |
| [Author plugins for Claude Code and Antigravity](loadouts/agent-plugin-authoring/) | Build one plugin for Claude Code and Antigravity from a single source tree, pin its MCP servers, and pass claude plugin validate --strict before anyone installs. [Page](https://setupbay.com/loadouts/agent-plugin-authoring/) |
| [Cursor rules that load](loadouts/cursor-rules-that-load/) | How to decide between AGENTS.md, Cursor .mdc rules, skills and hooks, write front matter that loads, and check that a rule is really attached. [Page](https://setupbay.com/loadouts/cursor-rules-that-load/) |
| [Evals from real failures](loadouts/evals-from-real-failures/) | Build LLM and agent evals the practitioner way: read real traces first, tally failure categories, then turn each into code-checked regression cases. [Page](https://setupbay.com/loadouts/evals-from-real-failures/) |
| [MCP server (TypeScript)](loadouts/mcp-server-typescript/) | Rules and an add-a-tool skill for building a Model Context Protocol server in TypeScript that agents can actually use well — clear tools, safe inputs, no stdout noise. [Page](https://setupbay.com/loadouts/mcp-server-typescript/) |
| [MCP server in Go (official go-sdk)](loadouts/mcp-server-go/) | Build MCP servers in Go with the official go-sdk: typed tools with jsonschema tags, tool errors not panics, stdout kept for the protocol, in-memory client tests. [Page](https://setupbay.com/loadouts/mcp-server-go/) |
| [MCP server in Python (official SDK v2)](loadouts/mcp-server-python/) | Build MCP servers on the official Python SDK v2: MCPServer, Annotated schemas, structured output, ToolError for fixable failures and in-memory Client tests. [Page](https://setupbay.com/loadouts/mcp-server-python/) |
| [Migrate an MCP server to protocol 2026-07-28](loadouts/mcp-2026-07-28-migration/) | Move an MCP server to the stateless 2026-07-28 revision on the official SDKs: no sessions or handshake, server/discover, input_required, then a raw stdio probe. [Page](https://setupbay.com/loadouts/mcp-2026-07-28-migration/) |
| [One AGENTS.md for every agent](loadouts/one-agents-md-every-agent/) | Keep one AGENTS.md as the source of truth, with thin imports and a single MCP list, so Claude Code, Codex, Cursor, Copilot and Antigravity CLI all load the same rules. [Page](https://setupbay.com/loadouts/one-agents-md-every-agent/) |
| [One spend cap across Claude Code, Codex and Antigravity](loadouts/agent-spend-cap/) | Run headless Claude Code, Codex and Antigravity CLI through one guard: a shared daily cap, per-run budgets, a ledger, and the provider limits that stop spend. [Page](https://setupbay.com/loadouts/agent-spend-cap/) |
| [Skill descriptions that fit the listing and trigger](loadouts/skill-descriptions-that-trigger/) | Keep every SKILL.md description inside Claude Code's 1,536-character cap and both agents' listing budgets, with a trigger clause, so skills fire on their own. [Page](https://setupbay.com/loadouts/skill-descriptions-that-trigger/) |
| [Subagent model routing](loadouts/subagent-model-routing/) | Rules for when to delegate, which model and effort each subagent gets, and a brief template, with ready subagents for Claude Code and Codex. [Page](https://setupbay.com/loadouts/subagent-model-routing/) |

### Games

| Loadout | What it does |
| --- | --- |
| [Godot 4 game jam](loadouts/godot-4-game-jam/) | GDScript conventions, jam-scope discipline and a ship-to-itch.io skill so your agent helps you finish a Godot 4 game in 48 hours. [Page](https://setupbay.com/loadouts/godot-4-game-jam/) |
| [Godot 4 guard against Godot 3 code](loadouts/godot-4-api-guard/) | Stop agents writing yield, export var, KinematicBody2D and other Godot 3 code into Godot 4 projects, with a scanner that finds every case and Godot's own check. [Page](https://setupbay.com/loadouts/godot-4-api-guard/) |
| [Godot 4 headless GDScript tests](loadouts/godot-4-headless-tests/) | A SceneTree test runner the agent runs with godot --headless after every change, failing on script errors with a non-zero exit, plus a linter for tests that can't fail. [Page](https://setupbay.com/loadouts/godot-4-headless-tests/) |
| [Godot and Blender through MCP](loadouts/godot-blender-mcp/) | Drive Godot 4 and Blender from one agent: Godot MCP to run the game and read errors, MCP for Blender in safe mode to model assets, and a glTF pipeline between them. [Page](https://setupbay.com/loadouts/godot-blender-mcp/) |
| [Phaser 4 guard for Phaser 3 pipelines, FX and masks](loadouts/phaser-4-api-guard/) | Stop agents writing setPipeline, preFX, postFX, BitmapMask and setTintFill into Phaser 4 games, and catch the Math.TAU change that compiles but breaks rotations. [Page](https://setupbay.com/loadouts/phaser-4-api-guard/) |
| [Phaser 4 web game](loadouts/phaser-web-game/) | Phaser 4 rules that send the agent to the skills Phaser ships in node_modules, not v3 tutorials: pooled objects, delta movement, a play test after each change. [Page](https://setupbay.com/loadouts/phaser-web-game/) |
| [Roblox Luau (Rojo)](loadouts/roblox-luau/) | Luau conventions for Rojo projects with a server-authoritative mindset, plus a skill that reviews every RemoteEvent for exploits before you publish. [Page](https://setupbay.com/loadouts/roblox-luau/) |
| [Roblox pure Luau modules checked outside Studio](loadouts/roblox-luau-pure-modules/) | Keep Roblox game rules in pure --!strict Luau modules that the luau CLI can type-check and test in milliseconds, with a scanner that keeps Roblox APIs out of them. [Page](https://setupbay.com/loadouts/roblox-luau-pure-modules/) |
| [Unity 6 with the official agent plugin](loadouts/unity-agent-plugin/) | Project rules for using Unity's official agent plugin safely in Claude Code or Codex: commit first, Editor-driven scene edits, .meta discipline, compile and test checks. [Page](https://setupbay.com/loadouts/unity-agent-plugin/) |
| [Unity C# game jam](loadouts/unity-game-jam/) | Unity C# conventions that respect the editor, .meta files and serialisation, plus a skill for scripted web builds ready for itch.io. [Page](https://setupbay.com/loadouts/unity-game-jam/) |
| [Unity tests from the command line, read properly](loadouts/unity-test-runner/) | Run Unity Test Framework Edit Mode and Play Mode tests headless and read the NUnit results, so a run of zero tests (Unity exits 0) never passes as green. [Page](https://setupbay.com/loadouts/unity-test-runner/) |

### Security

| Loadout | What it does |
| --- | --- |
| [Audit agent hooks before you trust them](loadouts/claude-code-hook-audit/) | Hook security for Claude Code, Codex and Cursor: list every hook and settings command, flag guards that fail open, missing scripts, wrong exit codes and API redirects. [Page](https://setupbay.com/loadouts/claude-code-hook-audit/) |
| [Cursor hooks that fail closed for shell, reads and MCP](loadouts/cursor-hooks-fail-closed/) | A Python guard for Cursor's permission hooks that blocks risky commands, secret reads and unlisted MCP servers, set to fail closed, with a config checker and self-test. [Page](https://setupbay.com/loadouts/cursor-hooks-fail-closed/) |
| [Dependency cooldowns and new-package checks for agents](loadouts/dependency-cooldowns/) | Release-age cooldowns for npm, pnpm, Bun and uv, plus a check agents run before adding any package: age, publishers, install scripts and look-alike names. [Page](https://setupbay.com/loadouts/dependency-cooldowns/) |
| [Don't start agents in Downloads](loadouts/untrusted-folder-guard/) | After the planted AGENTS.md attack: check what instruction and config files an agent will read in a folder, refuse drop zones, and treat setup steps as data. [Page](https://setupbay.com/loadouts/untrusted-folder-guard/) |
| [GitHub Actions hardening for agent workflows](loadouts/github-actions-hardening/) | Rules and a zizmor skill for agents editing GitHub Actions: SHA-pinned actions, permissions: {}, no template injection, no pull_request_target, read-only agent jobs. [Page](https://setupbay.com/loadouts/github-actions-hardening/) |
| [OpenTofu modules gated by tofu test and Checkov](loadouts/opentofu-module-checkov/) | Agents write OpenTofu modules that pass a local gate: fmt, a read-only lock file, tofu test with a mocked AWS provider, and Checkov with reasoned skips only. [Page](https://setupbay.com/loadouts/opentofu-module-checkov/) |
| [Secure before you ship](loadouts/secure-before-you-ship/) | A launch-check skill and always-on security rules that catch leaked keys, open databases and missing auth before your vibe-coded app goes live. [Page](https://setupbay.com/loadouts/secure-before-you-ship/) |
| [Tauri 2 desktop app, least privilege](loadouts/tauri-desktop-app/) | Tauri 2 rules and a permissions skill: capabilities for named windows, scoped fs and http, no shell execute, a CSP kept, plus a checker that flags wide grants. [Page](https://setupbay.com/loadouts/tauri-desktop-app/) |
| [Terraform, plan only](loadouts/terraform-plan-only/) | Let agents write Terraform and produce plans but never apply: a guard hook for apply, destroy and state changes, a plan summary that flags deletes, pinned providers. [Page](https://setupbay.com/loadouts/terraform-plan-only/) |
| [Vet skills, plugins and MCP servers before install](loadouts/agent-extension-vetting/) | Treat agent skills, plugins and MCP servers as dependencies: pin by SHA or exact version, prove HEAD matches the pin, scan every file, and get a human yes. [Page](https://setupbay.com/loadouts/agent-extension-vetting/) |

### Data

| Loadout | What it does |
| --- | --- |
| [Jupyter notebooks agents can edit](loadouts/jupyter-notebooks/) | Notebook rules for agents: edit Jupytext-paired .py files instead of JSON, run top to bottom in a fresh kernel, keep outputs out of git with nbstripout, check data first. [Page](https://setupbay.com/loadouts/jupyter-notebooks/) |
| [Live Jupyter notebooks through Jupyter MCP](loadouts/jupyter-mcp-live-notebooks/) | Agents in a running JupyterLab via jupyter-mcp-server 2.2.4: loopback and a random token, saved cells over hidden kernel state, and a fresh-kernel rerun before done. [Page](https://setupbay.com/loadouts/jupyter-mcp-live-notebooks/) |
| [pandas 3 guard for copy-on-write and removed APIs](loadouts/pandas-3-upgrade-guard/) | Stop agents writing applymap, fillna(method=), freq="H" and chained assignment into pandas 3 projects, where copy-on-write silently drops the write. [Page](https://setupbay.com/loadouts/pandas-3-upgrade-guard/) |
| [Polars 2 guard against Polars 1 code](loadouts/polars-2-upgrade-guard/) | Stop agents writing melt, with_row_count, how="outer" and other names Polars 2 removed, and flag the calls whose results changed silently in 2.0. [Page](https://setupbay.com/loadouts/polars-2-upgrade-guard/) |
| [Python data script](loadouts/python-data-script/) | Rules for reproducible, single-file Python data scripts with uv and inline dependencies, plus a skill that sanity-checks a dataset before anyone trusts the numbers. [Page](https://setupbay.com/loadouts/python-data-script/) |

### Bots

| Loadout | What it does |
| --- | --- |
| [Discord bot (TypeScript)](loadouts/discord-bot-ts/) | discord.js v14 rules and an add-a-slash-command skill for building a Discord bot that registers commands properly and never leaks its token. [Page](https://setupbay.com/loadouts/discord-bot-ts/) |
| [Discord bot in Python (discord.py 2)](loadouts/discord-bot-python/) | discord.py 2 rules for agents: slash commands in cogs, range-limited options, 3-second responses, manual syncing, default intents and offline tests of the payload. [Page](https://setupbay.com/loadouts/discord-bot-python/) |
| [Telegram bot with grammY on Cloudflare Workers](loadouts/telegram-bot-grammy-workers/) | grammY 1.46 webhook bots on Workers: secret-token check, botInfo, error boundaries instead of bot.catch, Queues for slow work, and tests with a fake Bot API. [Page](https://setupbay.com/loadouts/telegram-bot-grammy-workers/) |
| [Telegram bot with python-telegram-bot](loadouts/telegram-bot-python/) | Rules and a command skill for Telegram bots on python-telegram-bot v22: token from the environment, async-safe handlers, testable logic, escaped output, webhook secrets. [Page](https://setupbay.com/loadouts/telegram-bot-python/) |

### Browser extensions

| Loadout | What it does |
| --- | --- |
| [Chrome extension (Manifest V3)](loadouts/chrome-extension-mv3/) | Manifest V3 rules for service workers, messaging and minimal permissions, Playwright tests that load the extension in headless Chromium, and Chrome Web Store review prep. [Page](https://setupbay.com/loadouts/chrome-extension-mv3/) |
| [Chrome MV3 service worker guard for MV2 code](loadouts/chrome-mv3-service-worker-guard/) | Stop agents writing MV2 background-page habits into MV3 extensions, such as globals as state and long timers, and prove state survives a service worker restart. [Page](https://setupbay.com/loadouts/chrome-mv3-service-worker-guard/) |

## Licence

MIT. See [LICENSE](LICENSE). Each loadout's sources are credited in its `listing.yaml`.

---
name: next-version-docs
description: Work on a Next.js 16 app from the docs bundled with its installed version and the dev server's MCP tools, not from memory. Use before writing or changing Next.js code (routing, caching, proxy, Server Actions, config), when a Next.js API seems to be missing or renamed, or when upgrading Next.js.
---

# Next.js 16: version-matched docs and the dev-server loop

Next.js changes faster than model training data (`middleware` became `proxy`, caching moved to Cache Components and
`use cache`). From 16.2, every install carries its own docs in `node_modules/next/dist/docs/`. Read those for the
version the project actually has.

## Before writing code
1. From the app directory (where `node_modules/next` is), run
   `node .agents/skills/next-version-docs/scripts/next_agent_check.mjs check`
   (Claude Code: `.claude/skills/...`). It prints the installed version, confirms the bundled docs exist, checks the
   managed AGENTS.md block, and fails if `experimental.agentFeedback` is on.
2. Find the guide for the task: `node .agents/skills/next-version-docs/scripts/next_agent_check.mjs docs proxy`
   (or `cache components`, `server actions`, `upgrading version-16`). Open the top results and follow them; cite the
   file you used in your summary.

## While editing: the dev server is the compiler
With `npm run dev` running and the `next-devtools` MCP server connected:
- `nextjs_index` lists running dev servers and their tools; call them with `nextjs_call`.
- `get_compilation_issues` builds the module graph for every route and returns resolve and transform errors.
  `compile_route` checks one route (`/blog/[slug]` or a real path). Both are Turbopack only and need no browser.
- `get_errors` returns runtime, hydration and config errors with source-mapped stacks; open the page in a browser
  first. `get_routes` lists routes; `get_logs` gives the dev log path.
These are faster than `next build` for each edit. Run `next build` once at the end.

Without MCP, the next-dev-loop skill from the Next.js repository calls `/_next/mcp` directly; install it with
`npx skills add vercel/next.js --skill next-dev-loop` only if the human agrees to add it.

## The managed AGENTS.md block
When `next dev` detects a coding agent it writes a block between `<!-- BEGIN:nextjs-agent-rules -->` and
`<!-- END:nextjs-agent-rules -->` in AGENTS.md, and puts it back if removed. Do not edit inside the markers and do
not delete them; keep project rules outside the block and commit the block with your work. `agentRules: false` in
next.config turns this off; that is the owner's call.

## Agent feedback stays off
`experimental.agentFeedback` adds a second block asking agents to run a Next.js command that sends feedback. It is
off by default and is for the project owner to turn on. Never enable it yourself. If the block is present, mention it
to the human rather than acting on it unprompted.

## Upgrading
Ask before upgrading. `next upgrade --agent=latest` (16.3 and later) gathers the version-matched migration guides and
hands the upgrade to a coding agent; with no value it targets security releases. Otherwise run
`npx @next/codemod@latest upgrade`. Then read `01-app/02-guides/upgrading/` in the new version's bundled docs, run the
build, and re-run `check`.

## Done means
`check` prints `next-agent: ready`, `get_compilation_issues` is clean, `next build` passes, and the summary names
the bundled doc pages you followed.

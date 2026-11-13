# AGENTS.md: Markdown docs that stay correct

This repository keeps its documentation in Markdown: the root README and pages under `docs/`. Docs are reviewed
like code: links, anchors and commands must be right, not just readable.

## Commands

- Style: `npx markdownlint-cli2` (config in `.markdownlint-cli2.jsonc`).
- Links, anchors and script commands: `node .agents/skills/docs-check/scripts/check_docs.mjs` (offline).
- Done means: both are clean.

## Rules

- Use the `docs-check` skill whenever you add or edit Markdown.
- Every command in the docs is one you ran or copied from `package.json`. Never invent a script, flag or
  environment variable.
- Fenced code blocks name their language.
- When a heading or file is renamed, fix every link to it in the same change.
- Relative links between docs pages. External links only to official or primary sources.
- Do not add markdownlint disable comments to get a clean run.
- Keep the README short: what it is, quick start, where the docs are. Detail goes in `docs/`.

---
name: docs-check
description: Check Markdown docs before calling a docs change done - markdownlint-cli2 for style, and an offline check that relative links, images and #anchors resolve and that npm run commands in the docs exist. Use when writing or editing README files, docs/ pages, or anything that links between Markdown files.
---

# Docs check

Agents write docs that read well and are wrong in small ways: a link to a page that was renamed, an anchor
that no longer matches its heading, `npm run deploy` when there is no deploy script. Two checks catch these
without the network.

## Run both

```bash
npx markdownlint-cli2                                         # style; config in .markdownlint-cli2.jsonc
node .agents/skills/docs-check/scripts/check_docs.mjs         # links, anchors, script commands
```

`check_docs.mjs` takes paths (files or folders); with none it checks the root README and `docs/`.
Output is `file:line: problem` and a summary line; exit 1 means fix before finishing.

## What check_docs.mjs checks

- Relative links, images and reference definitions point at files that exist. A leading `/` means the
  repository root.
- A `#fragment` matches a heading in the target file, using GitHub's slug rules: lower case, punctuation
  dropped, spaces to hyphens, `-1`, `-2` for repeated headings. Explicit `<a id="...">` anchors count too.
- Every `npm run`, `pnpm run`, `yarn run` or `bun run` command in a code block or inline code names a script
  in the nearest `package.json`.
- External URLs are not fetched. Leave those to a scheduled link checker so a flaky site never blocks a change.

## Markdownlint config

Start from `references/markdownlint-cli2.jsonc` (copy it to the repository root as
`.markdownlint-cli2.jsonc`). It keeps the defaults and adds:

- MD040: every fenced block names its language (`bash`, `json`, `text` ...), so readers and highlighters know
  what it is.
- MD051: link fragments in the same file must match a heading.
- MD013 off (no hard wrapping of prose), MD024 only for sibling headings, a small HTML allow-list.

## Writing rules

- Commands in docs are commands you ran. Copy them from `package.json` scripts or your terminal, not memory.
- When you rename a heading or move a file, search for links to it (`rg -n 'old-slug|old-file.md'`) and fix
  them in the same change.
- Link with relative paths between docs files, never to the rendered GitHub URL of the same repository.
- Do not disable a markdownlint rule inline to get a clean run. Fix the Markdown, or change the shared config
  with a reason in the pull request.

## Done means

Both commands are clean, and the summary line from `check_docs.mjs` is in your report.

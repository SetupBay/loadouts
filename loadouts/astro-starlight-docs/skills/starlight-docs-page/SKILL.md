---
name: starlight-docs-page
description: Add, move or rewrite a page in an Astro Starlight docs site (Starlight 0.42, Astro 7) so it has proper front matter, links that the validator can check, and a passing build. Use for any change under src/content/docs/ or to the Starlight config.
---

# Write a Starlight docs page

## Before you start
- Check versions in `package.json`. This skill assumes `astro` 7.x and `@astrojs/starlight` 0.42.x. If they are older,
  stop and tell the human: upgrades go through `npx @astrojs/upgrade`, which moves both together.
- Check `astro.config.mjs` has `starlight-links-validator` and `starlight-llms-txt` in Starlight's `plugins`, and a
  real `site` URL. If not, show the human the diff against `references/astro.config.mjs` and ask before adding them
  (they are new dependencies).

## Steps
1. Pick the path. The file path is the URL, so `src/content/docs/guides/tide-alerts.md` becomes `/guides/tide-alerts/`.
   Moving a file changes its URL: search for links to the old URL and update them in the same change.
2. Write the front matter:
   ```yaml
   ---
   title: Tide alerts
   description: Get an email before high water at one port, with the threshold and lead time you choose.
   ---
   ```
   Optional fields that matter: `sidebar: { order: 2 }` to sort, `draft: true` to keep a page out of production builds,
   `template: splash` for a landing page without sidebars.
3. Write the body from `##` down. One idea per section; headings become anchors (`## Tide object` is `#tide-object`).
4. Link with root-relative page URLs and a trailing slash: `[API reference](/reference/api/#tide-object)`. No `.md`
   links, no `../`, no absolute links to the docs' own domain (the validator can't check those).
5. Images: put them in the project's src/assets folder and reference them with a relative path so Astro optimises them, or in `public/` for files that must keep their name. Always write alt text.
6. If the page belongs in a hand-written sidebar group, add it to `sidebar` in `astro.config.mjs`. Folders listed with
   `items: [{ autogenerate: { directory: "..." } }]` pick it up on their own.

## Prove it
```sh
node .agents/skills/starlight-docs-page/scripts/docs_lint.mjs src/content/docs --site https://docs.example.com
npm run build
```
The lint must report `0 to fix` and the build must end with `All internal links are valid.` If the validator reports
`invalid hash`, the heading text changed or never existed; fix the link, not the heading, unless the human agrees.
Check `dist/llms.txt` lists the docs if you changed the site title or added a section.

## Don't
- Don't hand-write `<h1>` or `# ` headings in a page.
- Don't turn off the links validator to get a build through.
- Don't add a Starlight plugin or integration without asking. Each one is a dependency with its own release cycle.

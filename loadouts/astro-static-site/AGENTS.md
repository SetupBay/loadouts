# AGENTS.md: Astro static site

Static output (`output: "static"`, the default). The built site is plain HTML/CSS in `dist/`.

## Principles
- **Ship no JavaScript unless a feature needs it.** `.astro` components render to HTML at build time.
  A UI framework component (React, Svelte, Vue) only runs in the browser with a `client:*` directive — use
  `client:visible` or `client:idle` over `client:load`, and only for genuinely interactive parts.
- Small inline `<script>` tags in `.astro` files are fine for simple interactivity (menus, copy buttons). Astro bundles them.
- Do not add a UI framework integration just for one widget.

## Layout
```
src/pages/          routes (file-based). [slug].astro + getStaticPaths for dynamic pages
src/layouts/        page shells (Base.astro holds <head>, meta tags, header, footer)
src/components/     .astro components
src/content/        markdown/MDX/JSON content
src/content.config.ts   collection definitions with zod schemas
src/styles/         global CSS (tokens as custom properties)
public/             copied as-is: favicon, robots.txt, _headers, _redirects
```

## Content collections
- Anything list-like (posts, projects, docs) is a collection defined in `src/content.config.ts` with a `glob()` loader and a `schema`.
- Read with `getCollection("blog")` / `getEntry(...)`; render markdown with `render(entry)`.
- Add new frontmatter fields to the schema first. The build should fail on bad content, not render `undefined`.

## Pages and SEO
- Every page sets a unique `<title>` and `<meta name="description">` via the layout props.
- Set `site` in `astro.config.mjs` so canonical URLs, sitemaps and RSS work.
- Use `@astrojs/sitemap` for a sitemap; add `robots.txt` in `public/`.
- Internal links are root-relative (`/about/`). Respect the configured `trailingSlash` setting.

## Images and assets
- Local images live in `src/assets/` and go through `<Image />` / `<Picture />` from `astro:assets` (sizes, formats, lazy loading).
- Always set meaningful `alt` text (empty `alt=""` for decorative images).
- Self-host fonts or use system fonts; preload only the one font file used above the fold.

## HTML and CSS
- Semantic HTML: one `<h1>`, landmarks (`header`, `main`, `nav`, `footer`), real `<button>`s and `<a>`s.
- Component styles in `<style>` (scoped by default). Global tokens (colours, spacing, fonts) as CSS custom properties.
- Check colour contrast and visible focus states. Respect `prefers-reduced-motion`.

## Before you say "done"
`npm run build` passes with no warnings you introduced, and `npm run preview` shows the change. Mention any new page or route.

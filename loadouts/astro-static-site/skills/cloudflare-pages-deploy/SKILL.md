---
name: cloudflare-pages-deploy
description: Deploy a static site (Astro, Vite or plain HTML) to Cloudflare Pages, with headers, redirects and a custom domain. Use when the user asks to deploy, host or publish a static site on Cloudflare.
---

# Deploy a static site to Cloudflare Pages

## 1. Confirm the build
- Build command and output folder: Astro `npm run build` → `dist`; Vite `npm run build` → `dist`; plain HTML: no build, output is the folder.
- Run the build locally and check the output folder has `index.html`.
- Set the Node version Cloudflare should use: add a `.nvmrc` (e.g. `22`) or the `NODE_VERSION` environment variable in the project settings.

## 2. Add Pages config files to `public/` (copied into the output)
`public/_headers`:
```
/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: DENY

/_astro/*
  Cache-Control: public, max-age=31536000, immutable
```
`public/_redirects` (only if needed):
```
/old-page /new-page/ 301
```

## 3. Choose a deploy route (ask the human which they prefer)
**A. Git integration (recommended for ongoing sites):** the human connects the repo in the Cloudflare dashboard
(Workers & Pages → Create → Pages → Connect to Git), sets the build command and output directory from step 1.
Every push to the production branch deploys; other branches get preview URLs.

**B. Direct upload with Wrangler:**
```sh
npx wrangler login                     # human does this once, in a browser
npx wrangler pages project create <project-name> --production-branch main
npx wrangler pages deploy dist --project-name <project-name>
```
Never paste or store a Cloudflare API token in the repo. In CI, use the `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` secrets.

## 4. Custom domain
In the Pages project → Custom domains → add `sub.example.com`. If the zone is on the same Cloudflare account, the DNS record is
created automatically; otherwise the human adds a CNAME to `<project>.pages.dev`. Certificates take a few minutes.

## 5. Verify
- Open the `*.pages.dev` URL and the custom domain. Check a deep link, the 404 page, and response headers
  (`curl -sI https://sub.example.com/ | grep -i x-content-type`).

## 6. Report
Project name, production URL, preview URL pattern, and anything the human still needs to click.

#!/usr/bin/env node
// Lint Starlight content pages for what the build doesn't check. Node standard library only.
//   node docs_lint.mjs [src/content/docs] [--site https://docs.example.com]
// fix:  missing title or description, a "# " heading in the body (Starlight renders the title as the h1),
//       links to .md files, images without alt text.
// warn: title over 60 or description outside 50-160 characters, absolute links to the docs' own site.
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const siteArg = args.includes("--site") ? args[args.indexOf("--site") + 1] : null;
const root = args.find((a, i) => !a.startsWith("--") && args[i - 1] !== "--site") ?? "src/content/docs";
const site = siteArg ? siteArg.replace(/\/$/, "") : null;

const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(path.join(d, e.name)) : /\.mdx?$/.test(e.name) ? [path.join(d, e.name)] : []));
const out = [];
let pages = 0;

for (const file of fs.existsSync(root) ? walk(root) : []) {
  pages++;
  const src = fs.readFileSync(file, "utf8");
  const m = src.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  const fm = m ? m[1] : "";
  const body = (m ? m[2] : src).replace(/```[\s\S]*?```/g, "");
  const field = (k) => {
    const r = fm.match(new RegExp(`^${k}:\\s*(.*)$`, "m"));
    return r ? r[1].trim().replace(/^["']|["']$/g, "") : null;
  };
  const rel = path.relative(process.cwd(), file);
  const title = field("title");
  const description = field("description");
  const isSplash = /^template:\s*splash/m.test(fm);
  if (!title) out.push(["fix", rel, "no title in front matter"]);
  else if (title.length > 60) out.push(["warn", rel, `title is ${title.length} characters; keep it under 60`]);
  if (!description) out.push(["fix", rel, "no description: search results and llms.txt fall back to nothing useful"]);
  else if (description.length < 50 || description.length > 160) out.push(["warn", rel, `description is ${description.length} characters; aim for 50-160`]);
  if (!isSplash && /^# \S/m.test(body)) out.push(["fix", rel, "has a '# ' heading; the title is already the h1, so start sections at '##'"]);
  for (const [, link] of body.matchAll(/\]\(([^)\s]+)\)/g)) {
    if (/^(?!https?:)[^#?]*\.mdx?(#|$)/.test(link)) out.push(["fix", rel, `links to a source file (${link}); link to the page URL, such as /guides/setup/`]);
    if (site && link.startsWith(site)) out.push(["warn", rel, `absolute link to this site (${link}); use a root-relative path so the links validator checks it`]);
  }
  for (const [, alt] of body.matchAll(/!\[([^\]]*)\]\(/g)) if (!alt.trim()) out.push(["fix", rel, "image without alt text"]);
}

for (const [level, file, msg] of out) console.log(`${level.padEnd(4)} ${file}: ${msg}`);
const n = (l) => out.filter((o) => o[0] === l).length;
console.log(`pages: ${pages}; ${n("fix")} to fix, ${n("warn")} warnings`);
process.exit(n("fix") || !pages ? 1 : 0);

#!/usr/bin/env node
// Look up an npm package before adding it: how old the version is, who publishes it, install scripts, look-alike
// names. Node standard library only (global fetch). Read-only: it never installs anything.
//   node pkg_check.mjs <name>[@version] [--min-days 7] [--registry https://registry.npmjs.org]
// Verdicts: ok, ask (show the human the reasons first), hold (too new for the cooldown; wait or ask).
const args = process.argv.slice(2);
const opt = (k, d) => (args.includes(k) ? args[args.indexOf(k) + 1] : d);
const spec = args.find((a, i) => !a.startsWith("--") && !["--min-days", "--registry"].includes(args[i - 1]));
if (!spec) {
  console.error("usage: node pkg_check.mjs <name>[@version] [--min-days 7] [--registry URL]");
  process.exit(2);
}
const minDays = Number(opt("--min-days", "7"));
const registry = opt("--registry", process.env.npm_config_registry || "https://registry.npmjs.org").replace(/\/$/, "");
const at = spec.lastIndexOf("@");
const [name, wanted] = at > 0 ? [spec.slice(0, at), spec.slice(at + 1)] : [spec, null];

// Popular names that typosquats imitate. Short on purpose: it catches the classic one-edit look-alikes
// (a letter added, dropped, changed or two letters swapped).
const POPULAR = ["react", "react-dom", "express", "lodash", "axios", "chalk", "commander", "debug", "dotenv", "eslint",
  "typescript", "vite", "vitest", "jest", "next", "vue", "zod", "prettier", "webpack", "moment", "dayjs", "uuid",
  "request", "colors", "yargs", "glob", "rimraf", "semver", "ws", "cors", "body-parser", "nodemon", "esbuild", "tsx",
  "playwright", "puppeteer", "openai", "@anthropic-ai/sdk", "wrangler", "astro"];
const lev = (a, b) => {
  const d = Array.from({ length: a.length + 1 }, (_, i) => [i, ...Array(b.length).fill(0)]);
  for (let j = 1; j <= b.length; j++) d[0][j] = j;
  for (let i = 1; i <= a.length; i++)
    for (let j = 1; j <= b.length; j++) {
      d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) d[i][j] = Math.min(d[i][j], d[i - 2][j - 2] + 1);
    }
  return d[a.length][b.length];
};

const res = await fetch(`${registry}/${name.replace("/", "%2f")}`, { headers: { accept: "application/json" } });
if (res.status === 404) {
  const near = POPULAR.filter((p) => p !== name && lev(p, name) <= 2);
  console.log(`not found: ${name} is not on the registry${near.length ? `; did you mean ${near.join(" or ")}?` : ""}`);
  console.log("verdict: ask");
  process.exit(1);
}
if (!res.ok) {
  console.error(`registry error ${res.status} for ${name}`);
  process.exit(2);
}
const doc = await res.json();
const version = wanted && doc.versions?.[wanted] ? wanted : doc["dist-tags"]?.latest;
const man = doc.versions?.[version];
if (!man) {
  console.log(`no version ${wanted ?? "latest"} for ${name}`);
  process.exit(1);
}
const days = (Date.now() - Date.parse(doc.time?.[version])) / 86400000;
const created = (Date.now() - Date.parse(doc.time?.created)) / 86400000;
const scripts = ["preinstall", "install", "postinstall", "prepare"].filter((s) => man.scripts?.[s]);
const near = POPULAR.filter((p) => p !== name && lev(p, name) === 1);
const reasons = [];
const hold = days < minDays;
if (hold) reasons.push(`version ${version} is ${days.toFixed(1)} days old; the cooldown is ${minDays} days`);
if (scripts.length) reasons.push(`runs install scripts: ${scripts.map((s) => `${s}: ${man.scripts[s]}`).join("; ")}`);
if (created < 30) reasons.push(`the package itself is ${created.toFixed(0)} days old`);
if (Object.keys(doc.versions ?? {}).length < 3) reasons.push(`only ${Object.keys(doc.versions ?? {}).length} version(s) published`);
if (!man.repository) reasons.push("no repository link");
if (near.length) reasons.push(`name is one edit away from ${near.join(", ")}`);
if (man.deprecated) reasons.push(`deprecated: ${man.deprecated}`);

console.log(`package: ${name}@${version}`);
console.log(`published: ${days.toFixed(1)} days ago; package created ${created.toFixed(0)} days ago; ${Object.keys(doc.versions ?? {}).length} versions`);
console.log(`maintainers: ${(doc.maintainers ?? []).map((m) => m.name).join(", ") || "none listed"}`);
console.log(`repository: ${typeof man.repository === "string" ? man.repository : man.repository?.url ?? "none"}`);
for (const r of reasons) console.log(`- ${r}`);
const verdict = hold ? "hold" : reasons.length ? "ask" : "ok";
console.log(`verdict: ${verdict}`);
process.exit(verdict === "ok" ? 0 : 1);

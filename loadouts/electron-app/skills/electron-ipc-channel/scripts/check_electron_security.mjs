#!/usr/bin/env node
// Static checks from the Electron security checklist. Pattern-based: it reads files, it runs nothing.
// Usage: node check_electron_security.mjs <dir> [more dirs]
// Exit 1 if anything is found. Checks .js/.mjs/.cjs/.ts/.tsx and .html files, skipping node_modules and build output.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const SKIP = new Set(["node_modules", "dist", "out", "build", ".git", ".vite", "release"]);
const CODE = /\.(?:[cm]?js|tsx?)$/;

function walk(dir, files = []) {
  for (const name of readdirSync(dir)) {
    if (SKIP.has(name)) continue;
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walk(p, files);
    else if (CODE.test(name) || name.endsWith(".html")) files.push(p);
  }
  return files;
}

const LINE_RULES = [
  [/\bnodeIntegration(?:InWorker|InSubFrames)?\s*:\s*true/, "nodeIntegration enabled: renderer code gets Node.js (checklist 2)"],
  [/\bcontextIsolation\s*:\s*false/, "contextIsolation disabled (checklist 3)"],
  [/\bsandbox\s*:\s*false/, "sandbox disabled (checklist 4)"],
  [/\bwebSecurity\s*:\s*false/, "webSecurity disabled (checklist 6)"],
  [/\ballowRunningInsecureContent\s*:\s*true/, "allowRunningInsecureContent enabled (checklist 8)"],
  [/\bexperimentalFeatures\s*:\s*true/, "experimentalFeatures enabled (checklist 9)"],
  [/\benableBlinkFeatures\s*:/, "enableBlinkFeatures used (checklist 10)"],
  [/\ballowpopups\b/, "allowpopups on a webview (checklist 11)"],
  [/@electron\/remote|\benableRemoteModule\s*:\s*true/, "remote module: renderer reaches main objects directly"],
  [/exposeInMainWorld\([^)]*\bipcRenderer\b\s*\)/, "ipcRenderer exposed to the renderer (checklist 20)"],
  [/exposeInMainWorld\([\s\S]*?\b(?:send|invoke|on)\s*:\s*\(\s*channel\b/, "renderer chooses the IPC channel name (checklist 20)"],
  [/\bipcRenderer\.(?:send|invoke)\(\s*channel\b/, "IPC channel name comes from a variable; use fixed names"],
  [/\bloadURL\(\s*["'`]http:\/\//, "loads content over plain HTTP (checklist 1)"],
  [/\bloadURL\(\s*["'`]file:\/\//, "file:// URL; serve the bundle from a custom protocol (checklist 18)"],
  [/\bRunAsNode\]\s*:\s*true/, "RunAsNode fuse left on (checklist 19)"],
  [/unsafe-eval/, "CSP allows unsafe-eval (checklist 7)"],
];

const findings = [];
const roots = process.argv.slice(2);
if (!roots.length) {
  console.error("usage: node check_electron_security.mjs <dir> [more dirs]");
  process.exit(2);
}
let mainFiles = 0;
let htmlFiles = 0;
for (const root of roots) {
  for (const file of walk(root)) {
    const rel = relative(process.cwd(), file);
    const text = readFileSync(file, "utf8");
    const lines = text.split("\n");
    lines.forEach((line, i) => {
      for (const [re, msg] of LINE_RULES) if (re.test(line)) findings.push(`${rel}:${i + 1}: ${msg}`);
    });
    if (file.endsWith(".html")) {
      htmlFiles++;
      if (!/Content-Security-Policy/i.test(text)) findings.push(`${rel}: no Content-Security-Policy meta tag (checklist 7)`);
      continue;
    }
    if (/new BrowserWindow\(/.test(text)) {
      mainFiles++;
      if (!/setWindowOpenHandler\(/.test(text)) findings.push(`${rel}: BrowserWindow without setWindowOpenHandler (checklist 14)`);
      if (!/["']will-navigate["']/.test(text)) findings.push(`${rel}: no will-navigate handler limiting navigation (checklist 13)`);
    }
    const handlers = [...text.matchAll(/ipcMain\.(?:handle|on)\(\s*["'`]([^"'`]+)["'`]\s*,\s*(?:async\s*)?\(([^)]*)\)\s*=>\s*\{([\s\S]*?)\n\}\);/g)];
    for (const [, channel, , body] of handlers) {
      if (!/senderFrame|assertTrustedSender|validateSender/.test(body)) findings.push(`${rel}: IPC handler "${channel}" does not check event.senderFrame (checklist 17)`);
    }
    for (const m of text.matchAll(/shell\.openExternal\(([^)]*)\)/g)) {
      const before = text.slice(Math.max(0, m.index - 300), m.index);
      if (!/^["'`]https:\/\//.test(m[1].trim()) && !/protocol|isAllowed|allowList|allowlist|startsWith\(\s*["'`]https:/.test(before)) {
        findings.push(`${rel}: shell.openExternal(${m[1].trim()}) without a URL check (checklist 15)`);
      }
    }
  }
}
for (const f of findings) console.log(f);
console.log(findings.length ? `${findings.length} finding(s)` : `ok: no findings (${mainFiles} window file(s), ${htmlFiles} HTML file(s))`);
process.exit(findings.length ? 1 : 0);

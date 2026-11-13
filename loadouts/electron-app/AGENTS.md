# AGENTS.md: Electron desktop app

Electron app: a privileged main process (Node.js) and renderer processes that show web content. Treat every renderer
as untrusted web content, even when it only loads your own bundle. Follow the Electron security checklist.

## Commands
- Check the project's `package.json` scripts first. Typical: `npm start` (dev), `npm test`, `npm run make` or
  `npm run dist` (packaging).
- Type-check with `npx tsc --noEmit` if the project uses TypeScript.
- Before finishing, run the `electron-ipc-channel` skill's security check (`scripts/check_electron_security.mjs` in the
  skill folder) over `src/`. It must report no findings.

## Windows (BrowserWindow and webPreferences)
- Keep the secure defaults and write them out so reviews can see them: `contextIsolation: true`, `sandbox: true`,
  `nodeIntegration: false`. Never set `webSecurity: false`, `allowRunningInsecureContent: true`,
  `experimentalFeatures: true` or `enableBlinkFeatures`.
- Load local pages from a custom protocol (`protocol.handle`) or the packaged file, never remote code into a window
  with a preload.
- Set `webContents.setWindowOpenHandler` to deny by default and open allowed links with `shell.openExternal` only
  after checking the URL scheme is `https:` (or a small allow-list).
- Handle `will-navigate` and block navigation away from the app's origin.
- Define a Content Security Policy (meta tag or response header): `default-src 'self'`, no `unsafe-eval`.

## Preload and IPC
- The preload exposes small, named functions through `contextBridge.exposeInMainWorld`. Never expose `ipcRenderer`,
  `require`, `process` or a generic "send any channel" function.
- Main uses `ipcMain.handle` for request/response. Every handler checks `event.senderFrame` (origin allow-list) and
  validates its arguments before doing anything.
- Do privileged work (files, shell, network with credentials) in main, never in the renderer.
- New channels: use the `electron-ipc-channel` skill.

## Packaging and updates
- Flip fuses at package time with `@electron/fuses`: `RunAsNode` off, `EnableNodeOptionsEnvironmentVariable` off,
  `EnableNodeCliInspectArguments` off, `EnableEmbeddedAsarIntegrityValidation` on, `OnlyLoadAppFromAsar` on,
  `EnableCookieEncryption` on.
- Stay on a supported Electron major. Ask before upgrading a major version; read the breaking changes first.
- Do not sign, notarise, publish or upload builds unless the user asks. Never commit signing certificates or tokens.

## Dependencies
- Ask before adding a dependency. Pin exact versions for anything that runs in main.
- No `@electron/remote`. No native modules unless needed and rebuilt for the Electron version.

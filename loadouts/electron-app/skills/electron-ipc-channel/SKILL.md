---
name: electron-ipc-channel
description: Add a typed IPC channel between an Electron renderer and the main process, with a narrow preload API, sender validation and argument checks, then run the security check.
---

# Add an IPC channel

The examples are in `references/`: `main.ts`, `preload.ts` and `renderer-api.d.ts`. Copy the pattern, not the
names.

1. Name the operation after what the user does (`notes:save`), not a generic verb (`send`, `invoke`).
2. Preload: add one function to the object passed to `contextBridge.exposeInMainWorld`. It calls
   `ipcRenderer.invoke` with a fixed channel name and passes only the arguments it needs. Never pass `ipcRenderer`
   itself, an event object, or a channel name chosen by the renderer.
3. Types: add the function to the `window` API declaration so the renderer gets type checking.
4. Main: register `ipcMain.handle(channel, handler)`. In the handler, first call `assertTrustedSender(event)`,
   which checks `event.senderFrame?.origin` against the app's own origin, then validate every argument (type, length,
   allowed values). Throw on bad input; Electron passes the error message to the renderer's promise.
5. Keep the work in main and return plain data (no class instances, functions or Electron objects).
6. Run `node scripts/check_electron_security.mjs src` and fix every finding. Run the type-check.

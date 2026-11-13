import { app, BrowserWindow, ipcMain, net, protocol, shell, type IpcMainInvokeEvent } from "electron";
import { join, normalize, sep } from "node:path";
import { pathToFileURL } from "node:url";

const APP_ORIGIN = "app://bundle";
const MAX_NOTE_CHARS = 10_000;
const RENDERER_DIR = join(__dirname, "renderer");
const notes = new Map<string, string>();

// Serve the bundle from app://bundle/ instead of file://, so only files under RENDERER_DIR are reachable.
protocol.registerSchemesAsPrivileged([{ scheme: "app", privileges: { standard: true, secure: true, supportFetchAPI: true } }]);

function serveBundle(request: Request): Promise<Response> | Response {
  const file = normalize(join(RENDERER_DIR, decodeURIComponent(new URL(request.url).pathname)));
  if (!file.startsWith(RENDERER_DIR + sep)) return new Response("not found", { status: 404 });
  return net.fetch(pathToFileURL(file).toString());
}

function assertTrustedSender(event: IpcMainInvokeEvent): void {
  const origin = event.senderFrame?.origin;
  if (origin !== APP_ORIGIN) throw new Error(`untrusted IPC sender: ${origin ?? "unknown"}`);
}

function parseNoteId(value: unknown): string {
  if (typeof value !== "string" || !/^[a-z0-9-]{1,64}$/.test(value)) throw new Error("invalid note id");
  return value;
}

ipcMain.handle("notes:save", (event, id: unknown, text: unknown) => {
  assertTrustedSender(event);
  const noteId = parseNoteId(id);
  if (typeof text !== "string" || text.length > MAX_NOTE_CHARS) throw new Error("invalid note text");
  notes.set(noteId, text);
  return { id: noteId, savedAt: new Date().toISOString() };
});

ipcMain.handle("notes:load", (event, id: unknown) => {
  assertTrustedSender(event);
  return notes.get(parseNoteId(id)) ?? null;
});

function isAllowedExternal(url: string): boolean {
  try {
    return new URL(url).protocol === "https:";
  } catch {
    return false;
  }
}

function createWindow(): BrowserWindow {
  const win = new BrowserWindow({
    width: 1000,
    height: 700,
    webPreferences: {
      preload: join(__dirname, "preload.js"),
      contextIsolation: true,
      sandbox: true,
      nodeIntegration: false,
    },
  });
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (isAllowedExternal(url)) void shell.openExternal(url);
    return { action: "deny" };
  });
  win.webContents.on("will-navigate", (event, url) => {
    if (!url.startsWith(`${APP_ORIGIN}/`)) event.preventDefault();
  });
  void win.loadURL(`${APP_ORIGIN}/index.html`);
  return win;
}

void app.whenReady().then(() => {
  protocol.handle("app", serveBundle);
  createWindow();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

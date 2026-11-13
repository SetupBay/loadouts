import { contextBridge, ipcRenderer } from "electron";

// Small, named functions only. The renderer never sees ipcRenderer or picks a channel name.
const api = {
  saveNote: (id: string, text: string): Promise<{ id: string; savedAt: string }> =>
    ipcRenderer.invoke("notes:save", id, text),
  loadNote: (id: string): Promise<string | null> => ipcRenderer.invoke("notes:load", id),
};

export type NotesApi = typeof api;

contextBridge.exposeInMainWorld("notes", api);

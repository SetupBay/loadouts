import type { NotesApi } from "./preload";

declare global {
  interface Window {
    notes: NotesApi;
  }
}

export {};

---
name: tauri-permissions
description: Add or change Tauri 2 capabilities with least privilege (named windows, scoped fs and http permissions, no broad shell access, CSP kept) and run the capability check. Use when a feature needs a new plugin or permission.
---

# Tauri permissions

1. Name the exact API the feature needs (for example "read one JSON file in the app data folder").
2. Find the narrowest permission for it in the plugin's permission list (in `src-tauri/gen/schemas/` after a build, or
   the plugin docs). Prefer a single `allow-<command>` permission to a plugin's `default` set.
3. Add it to a capability file for the named window, with a scope:

       { "identifier": "fs:allow-read-text-file", "allow": [{ "path": "$APPDATA/settings.json" }] }

4. Do not widen an existing capability's windows. If another window needs it, add a second capability.
5. Run the check: `node scripts/check-capabilities.mjs src-tauri`. It fails on wildcard windows with sensitive
   permissions, unscoped fs or http permissions, shell execute or spawn, remote URLs with commands, and a missing or
   null CSP. Fix every finding, or explain to the human why it is needed and get approval.
6. Run the app and use the feature once. Report the permissions added and why each is needed.

---
name: extension-store-prep
description: Prepare a Manifest V3 Chrome extension for Chrome Web Store submission. Use when the user wants to publish, submit, package or release their extension.
---

# Chrome Web Store prep

## 1. Audit the manifest
- `manifest_version` is 3, `version` is bumped since the last upload, `name` and `description` (≤132 chars) are final.
- Icons: 16, 32, 48 and 128 px PNGs exist and are referenced.
- For each permission and host permission, write a one-sentence justification describing the user-facing feature that needs it.
  If you cannot, recommend removing it. `activeTab` is preferred over host permissions; broad host permissions slow review.

## 2. Check for common rejection reasons
- **Remote code:** search the build for `eval(`, `new Function(`, remote `<script src=`, and imports from `http`. Any hit is a blocker.
- **Single purpose:** the extension does one clearly described thing. Flag unrelated features.
- **Obfuscation:** minified is fine, obfuscated is not. Do not enable obfuscating build plugins.
- **Data use:** list every piece of user data the extension reads, stores or sends anywhere.

## 3. Write the listing material into `store/`
- `store/description.md`: what it does in the first sentence, then features, then a privacy line.
- `store/permissions.md`: each permission with its justification (pasted into the dashboard's Privacy tab).
- `store/privacy.md`: data collected, why, where it goes, retention. If nothing leaves the device, say so plainly.
  A privacy policy URL is required if the extension handles personal or sensitive data — the human must host it somewhere.
- Screenshot list: tell the human to capture at least one 1280×800 (or 640×400) screenshot, plus a 440×280 small promo tile.

## 4. Package
```sh
npm run build
cd dist && zip -r ../extension-$(node -p "require('./manifest.json').version").zip . -x "*.map" && cd ..
```
`manifest.json` must be at the root of the zip. Exclude source maps and dev files.

## 5. Hand over
Tell the human the zip path, then the dashboard steps they must do themselves: upload at the Chrome Web Store Developer
Dashboard, fill in Store listing and Privacy tabs from the `store/` files, choose visibility, submit for review.
A one-off developer registration fee applies to new accounts. Do not claim the extension has been submitted.

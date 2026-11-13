---
name: unity-web-build
description: Build a Unity project for the web (WebGL) from the command line and prepare it for itch.io. Use when the user asks to build, export or upload their Unity game for the browser.
---

# Unity web build for itch.io

## 1. Add a build script (once)
Create `Assets/Editor/BuildScript.cs`:

```csharp
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

public static class BuildScript
{
    public static void BuildWeb()
    {
        PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Gzip;
        PlayerSettings.WebGL.decompressionFallback = true; // works on hosts without Content-Encoding headers

        var scenes = EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => s.path).ToArray();
        var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
        {
            scenes = scenes,
            locationPathName = "Build/Web",
            target = BuildTarget.WebGL,
            options = BuildOptions.None
        });

        Debug.Log($"Build {report.summary.result}: {report.summary.totalSize / (1024 * 1024)} MB");
        if (report.summary.result != BuildResult.Succeeded) EditorApplication.Exit(1);
    }
}
```

The human must have the **Web/WebGL Build Support** module installed for their editor version (Unity Hub → Installs → Add modules).
Scenes must be listed and ticked in Build Settings / Build Profiles.

## 2. Build in batch mode
Close the editor first (batch mode cannot open a project that is already open).

```sh
# Path to the editor varies: Unity Hub → Installs → ⋯ → Show in folder
"<path-to-Unity>" -batchmode -quit -projectPath . -executeMethod BuildScript.BuildWeb -logFile -
```
Exit code 0 means success. On failure, search the log for `error CS` (compile errors) or `Build Failed`.

## 3. Check and test
- `Build/Web` should contain `index.html`, `Build/` and `TemplateData/`.
- Serve locally (`npx serve Build/Web`) and ask the human to play for 30 seconds. Audio starts after the first click.
- If the build is over ~100 MB, suggest lowering texture max sizes and using compressed audio before upload.

## 4. Upload
- Zip the **contents** of `Build/Web` (so `index.html` is at the root of the zip), or use butler:
  `butler push Build/Web user/game-slug:html5`.
- On itch.io: Kind of project → HTML, tick "played in the browser", set the viewport to the canvas size, enable the fullscreen button.

## 5. Report
Build size, any warnings worth fixing, the upload channel, and the itch.io steps the human still needs to click.

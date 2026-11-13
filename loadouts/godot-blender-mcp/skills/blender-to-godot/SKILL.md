---
name: blender-to-godot
description: Model or adjust an asset in Blender through MCP, export it as glTF and bring it into a Godot 4 scene, then check it in the running game. Use when creating or updating a 3D asset for the Godot project.
---

# Blender to Godot

1. **Brief.** Restate the asset: purpose, size in metres, polygon budget, style references from `art/reference/`.
2. **Build in Blender** with the `blender` tools: block out, refine, materials. Look at the viewport from several angles
   after each step. Keep to `references/asset-checklist.md`.
3. **Prepare for export**: apply transforms, set the origin, name the object and its materials, remove unused data.
4. **Export** glTF binary to `assets/models/<name>.glb` inside the Godot project, selected objects only, +Y up.
   Use a short Blender script through the MCP tool if needed; safe mode allows normal export.
5. **Import in Godot.** Godot imports `.glb` on focus or project run. Instance it in the target scene with the `godot`
   scene tools (or a small `.tscn` edit), set collision if gameplay needs it.
6. **Run** the project through the `godot` server, read the debug output, and fix import or script errors.
7. **Report**: file paths, polygon count, any licence credits added to `art/CREDITS.md`, and what the human should look at.

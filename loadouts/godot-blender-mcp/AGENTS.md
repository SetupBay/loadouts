# AGENTS.md: Godot 4 and Blender through MCP

The agent drives two tools: Godot (MCP server `godot`: launch the editor, run the project, read debug output, create
scenes and nodes) and Blender (MCP server `blender`: inspect and change the open scene, run Python in safe mode, look at
the viewport). Assets move from Blender to Godot as glTF.

## Godot
- Run the project through the `godot` server after every gameplay change and read the debug output. Errors or warnings
  you caused are failures.
- Prefer editing `.gd` scripts and creating scenes through the server's scene tools. Hand-edit `.tscn` only for small,
  obvious changes; keep `uid://` references intact.
- Typed GDScript (`var speed: float = 200.0`), signals for decoupling, one responsibility per scene.
- If the server cannot find Godot, ask the human to set `GODOT_PATH` to the Godot executable in the MCP config.

## Blender
- The human saves the `.blend` before you start. You never save over it without asking; save variants as `<name>-v<n>.blend`.
- Safe mode stays on (`BLENDER_MCP_SAFE_MODE=1`): scripts that touch files, the network or other programs are blocked.
  Do not ask to turn it off. If a blocked script is needed, explain why and let the human decide.
- After every change, use the viewport look tool to check the result before continuing.
- Match the style in `art/reference/` (images the human provides): palette, proportions, polygon budget. Look at them first.
- Keep models game-ready: applied transforms, origin at the base, real-world scale (1 unit = 1 m), named objects and
  materials, modest polygon counts.
- Imported third-party assets keep their licence and credit. Record source and licence in `art/CREDITS.md`.

## Blender → Godot
Use the `blender-to-godot` skill for every asset that moves between the two.

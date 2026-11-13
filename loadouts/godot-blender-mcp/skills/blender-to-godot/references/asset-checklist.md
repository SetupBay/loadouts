# Game-ready asset checklist

- [ ] Scale: 1 Blender unit = 1 metre; a door is about 2 m tall
- [ ] Transforms applied (location, rotation, scale); origin at the base or the pivot gameplay needs
- [ ] Object, mesh and material names are meaningful (`crate_wood`, not `Cube.004`)
- [ ] Polygon count within the brief's budget; no hidden or duplicate geometry
- [ ] Normals face outwards; smooth/flat shading chosen on purpose
- [ ] Materials use Principled BSDF with image textures (these export cleanly to glTF)
- [ ] Textures packed or saved next to the `.glb`, power-of-two sizes
- [ ] Exported as `.glb`, selected objects only, +Y up
- [ ] Third-party assets: source and licence recorded in `art/CREDITS.md`

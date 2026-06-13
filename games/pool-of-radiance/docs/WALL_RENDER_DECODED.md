# Pool of Radiance — 3-D wall rendering system (decoded 2026-06-12)

How the first-person city/dungeon view is built from decoded data. Cracked while improving the
reproduction's "too open" 3-D view.

## The three data layers
1. **8X8D{1..8}.DAX — the tile sets.** Each file has blocks `id=1,3,5` = sheets of **8×8 4bpp
   EGA tiles** (header byte 8 = count: 70 / 31 / 45 tiles). Block `id=201` is the font (separate).
   Tile **17** = the clean masonry stone-block (gray with mortar grid, tiles seamlessly); tile
   **13** = stone with a perspective-edge diagonal (used at wall corners, 247× in WALLDEF1#1);
   tiles 50/51 = wood/bars (doors), 16 = dark cobble, 1/3 = floor/horizon edges.
2. **WALLDEF{1..8}.DAX — wall composition tables** (3 blocks each, 780 bytes). A wall face is a
   **grid of 8×8 tile indices**. Row markers: `40`=row left-edge, `39`=row right-edge (a 40..39
   run = one horizontal course of 5–6 tiles); `18..19` / `18..20` = the angled/perspective row
   variant; runs of `1`/`3` separate wall definitions. WALLDEF1#1 parses to **44 rows** that
   assemble into ~6 wall faces (the left/right/front slots at the near distances). Rendered, the
   tiles compose into real gray stone-block masonry with cyan mortar — confirms the decode.
3. **GEO plane2 (per cell) — which wall set / backdrop** a cell uses (0x00 open street, 0x8x
   building variants, 0x0B alt ground). See [[MANUAL_DECODED]] / project memory.

## BACPAC.DAX = wilderness terrain tiles (NOT the city backdrop)
40 tiles of 24×24 (header count=40, width=24): grass (bright green), rock/dirt (brown), boulders
(gray), water (cyan/white). These are the **overhead Wilderness map** terrain icons, not the
3-D city backdrop. Set aside for the city view.

## What the reproduction does with it (approximate.html)
- Walls: real tile-17 stone texture, tiled across each perspective face at a distance-scaled block
  size (`ts = F/z·0.20`), clipped to the eye-projection trapezoid, distance-darkened. Exported by
  `export_game.py` as `wallTile`/`wallStrip`.
- Floor: tile-17/18 cobblestone, drawn as perspective depth-bands (`floorTile`) — fixes the
  "too open / empty void" feel by giving the plaza a visible paved street.
- Sky/ceiling: dim gradient (city blocks are open-air).

## WALLDEF block internals (decoded 2026-06-12)
A 780-byte WALLDEF block = one wall set's faces, as **5 pairs of {side-def, front-def}** (one pair
per view distance). Each pair: a 13-byte header (`1 1 1` terminator) then the face's tile-grid
rows. Front-def rows are width-5 (`40 t t t t t 39`), side/angled-def rows use the `18..19/20`
markers. Section offsets in WALLDEF1#1: 13/61, 169/217, 325/373, 481/529, 637/685.
- The **plain front wall** (e.g. section 61) is built from **tile 13** = the game's diagonal-
  *beveled* gray masonry (3-D shaded). This is the real wall surface — the reproduction now uses
  it (was using flat mortar tile 17).
- **Archway/door face** (section 373): `40 69 70 70 70 68 39` (arch top) then `40 50 0 0 0 51 39`
  rows = left-frame tile 50, **opening = tile 0 (transparent)**, right-frame tile 51.
- Some faces reference tile indices >69 → they pull from the **other 8X8D blocks** (id 3/5 =
  tiles 70-139/140-209) or the windows/feature tiles — full per-type face compositing needs that
  cross-block index resolved.

## Renderer machine code (disassembled from GAME.OVR — the "raw crack")
- **Loaders** (unit 0x3bd): `LoadWallSet` builds `WALLDEF%d.dax`, `Load3DMap` builds `GEO%d.dax`
  (strings @0x2f6ac / 0x2f995). The area picks a wall-set number → loads that WALLDEF file.
- **Blitter** (unit 0x3b0): the planar VGA blit is `lcall 0x709:0x1df` (Sequencer Map-Mask). The
  wall-tile draw routine @unit+0x2a0 calls it 3×; its ABI takes a per-wall struct (ptr at [bp+6])
  whose fields are **column bounds** (`[di-0x65]`=left col, `[di-0x64]`=width) + **face/tile id**
  (`[di-0x53]`) + flags. So the 3-D view is composed on a **40-column grid** (constant `0x27`=39 =
  rightmost col; row constants `0x18`=24 and `0x20`=32 bound the wall band) — walls are drawn as
  column-range × row-range tile fills, NOT free pixel coords. This confirms the grid-compositor
  model and gives the real viewport metrics (40 cols).
- **Face vocabulary** (per WALLDEF block, 5 type-faces, all 5×7 tiles = the near slot): plain
  beveled stone (@529), wood door (@685), gate/portcullis (@373), window (@217, half-height
  4 rows), base-ledge (@61). The reproduction renders the real door/gate/base/plain faces by
  wall-type category; the byte-exact bitmaps are exported (wallFaceDoor/Gate/Window/Base/Plain).

## ⭐ Wall-type → face index — CRACKED
The 5 faces per WALLDEF block are stored in a fixed order **[base, window, gate, plain, door]**.
A GEO wall-type value **T (1-15)** maps as: **block = (T-1)//5** → WALLDEF block 1/3/5 (the
tileset/shade variant), **face = (T-1)%5** → the face in that order. Verified against the plane3
interactive-flag evidence across all levels: door-types 5/10/15 → `%5==4` = door ✓; plain-types
4/9/14 → `%5==3` = plain ✓; gate/arch-types 3/8/13 → `%5==2` = gate ✓. The reproduction uses this
exact index (`faceCat(type)`), rendering the real decoded face per wall-type.

## Bedrock: there is NO static slot-coordinate table (fully traced)
Chased the geometry to the bottom (unit 0x3b0 @0x0cb). The renderer is a **40-column text-grid
compositor**, not a coordinate-table system:
- Each wall row is a **40-char string**. The setup fn StrCopy's it into a local, FillChar-zeroes a
  40-byte column buffer, then scans the string char-by-char.
- A **character-set test** (`lcall 0xAF8:0xDC0` against the 32-byte bitset at unit cs:`0x0ab` =
  `00*6 ff 03 fe ff ff 07` = **digits '0'-'9' + letters 'A'-'Z'**) decides which chars are walls.
- Wall columns are recorded into the buffer (`[di-0x8f]`/`[di-0x8e]`), then the blitter
  (`0x709:0x1df`) fills each wall column-range across the wall-band rows (`0x18`=24 … `0x20`=32) on
  the 40-col grid (`0x27`=39 right edge).
So the per-depth "geometry" is **encoded in the wall-layout strings themselves** (exactly like the
WALLDEF face rows) — there is no hidden numeric slot array to dump. The reproduction's eye-
projection reproduces the same model (walls at columns, fixed wall-band height). Everything in the
wall-render pipeline is now decoded end-to-end: tiles → faces → type-index → grid compositor.

## Not yet done (full fidelity)
- Render the EXACT WALLDEF wall faces per screen slot (parse each definition's tile grid and map
  it to the left/right/front trapezoid at each distance) instead of a single tiled stone texture.
- Map plane2 0x8x variants → which WALLDEF set / which building facade (doors, windows, banners
  are all in the tile set: 50/51 wood, 46/47 windows, 38/37 banners).
- Distant building facades across open plaza cells; per-block indoor/outdoor ceiling choice.

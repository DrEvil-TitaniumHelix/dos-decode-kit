# Pool of Radiance (1988, SSI Gold Box) — Decode Findings

**Status:** data + asset + world layer DECODED and validated clean-room (2026-06-12 AM).
**Model:** decoded under Opus 4.8 (fallback) / Fable 5 — clean-room on facts, method carried from the Midwinter campaign.
**Ground truth:** the bytes themselves (hard oracles below) + shipped manuals (`Manual.pdf`, `Adventurers Journal.pdf`, `Cluebook.pdf`).

This engine is the **SSI Gold Box engine**, shared across ~12 games (Pool of Radiance,
Curse of the Azure Bonds, Secret of the Silver Blades, Pools of Darkness, the three
Krynn games, both Buck Rogers, the three Eye of the Beholder, Gateway to the Savage
Frontier). Everything below reads the data files of the whole family.

## Binary layout
- `START.EXE` (65 KB) — loader. `GAME.OVR` (206 KB) — Pascal-compiled engine overlay (NOT yet decoded; the hard x86 tier).
- 113 × `.DAX` data archives; `CHRDATA*.{SAV,ITM,SPC}` character records; `ITEMS`, `SAVGAMA.DAT`, `POOL.CFG`.

## 1. DAX archive container — DECODED (exact-fit on all 113 files)
```
offset 0:  u16  header  = 9 * block_count   (== directory byte length)
offset 2:  N × 9-byte directory entries:
             u8   id            (block id; high bit 0x80 = mirror/2nd-half variant)
             u32  offset        (LE, relative to start of data section)
             u16  unpacked_size (LE)
             u16  packed_size   (LE)
offset 2 + header:  data section (concatenated packed blocks)
```
**Validation oracle:** for every file, `2 + header + Σ packed_size == file_size`, and each
block's offset equals the running sum of prior packed sizes. Holds for 113/113 archives.

## 2. Block compression (RLE) — DECODED (1245/1245 blocks exact)
```
while input remains:
    c = next byte
    if c < 0x80:  copy (c + 1) literal bytes
    else:         repeat the next byte (256 - c) times
```
**Validation oracle:** decoded output length == directory `unpacked_size` for ALL 1245
blocks across all archives. No terminator; pure RLE.

## 3. EGA image format — DECODED (width-verified visually across 414 sprites)
```
u8  width_px        (header[0]; high byte header[1] = 0)
... 2 more header bytes (height/flags — height also derivable from block length)
pixel data: 4 bits/pixel, packed 2 px/byte, HIGH nibble first, standard 16-color EGA palette
```
Verified by rendering: at the header width the image resolves to a coherent sprite; any
other width shears into noise. CBODY = 128-frame player combat animation (weapon poses);
BODY1-8 / CPIC1-8 = monster combat sprites; CHEAD = portraits; COMSPR = tactical figures;
8X8D = wall-texture atlases (tile cell = 8px; sheet width needs a tiling pass).

## 4. GEO dungeon maps — STRUCTURALLY PLAUSIBLE, NOT YET CONFIRMED
Every GEO block is 1026 bytes = `u16 header + 1024 cells`. Two readings both fit:
- (A) 32×32 grid, 1 byte/cell, nibbles = south/east edge wall indices (half-grid storage)
- (B) 16×16 grid, 4 bytes/cell, one byte per N/E/S/W wall
Reading (A) renders maze-like rooms/corridors, but **this is not yet validated against a
known map.** "Looks like a dungeon" ≠ "is the dungeon." Pending: cross-check a rendered
GEO against the printed dungeon maps in `Cluebook.pdf` (ground truth) to confirm grid size,
nibble assignment, and orientation. DO NOT treat as decoded until that match is shown.

## Outlier formats — RESOLVED 2026-06-12 (Fable 5, second pass)
- **8X8D wall tiles — CRACKED.** 4bpp linear EGA with an **8-byte header** (the earlier 4-byte
  assumption was the bug). Real masonry/mortar/stonework at width ~16. Each block = a set of
  small wall-tile pieces; `WALLDEF*.DAX` (780-byte index tables) assemble them into the
  perspective view. Masonry texture extracted + applied to the reproduction walls.
- **ECL text — explained, not extracted.** ECL bytecode contains NO plaintext (confirmed by
  scanning every file). Header = `XX YY 01 01` offset/jump table + bytecode; room/encounter text
  is encoded inside the VM. Found the real text elsewhere: **ITEM1-4.DAX = the 110-item treasure
  database** (same 63-byte record format as CHRDATA.ITM) — decoded + wired as combat loot.
- **Class field — decoded to group level.** **CHRDATA offset 284 = AD&D class group**
  (9=Warrior, 6=Priest, 12=Rogue/Mage). Finer class from thief-skills (Thief vs MU in grp 12) +
  equipment + exceptional-STR (F vs F/MU in grp 9). RHIANNON resolves to Fighter/Magic-User.
  The exact within-group class is multi-byte; the group byte is the clean anchor.

## Other DAX groups (identified, not yet fully decoded)
- `ECL1-8.DAX` — ECL bytecode scripts (event/encounter/dialog VM). **Next logic target.**
- `8X8D*` wall-texture atlases pair with GEO wall indices to texture the 3D dungeon view.

## 5. GAME.OVR engine code — WALL BREACHED (not yet fully mapped)
- Container: **`FBOV`** = Borland/Turbo Pascal overlay. `dword@4` = 206097 ≈ file size.
  File start = length-prefixed Pascal string/data table (728 strings, incl. full credits,
  "version 1.3", every UI message). ASCII = only ~5% of file; rest is code+data interleaved.
- **NOT packed:** entropy uniform ~6.9 bits/byte (compressed would be >7.5). Zero `int 21h`
  (overlay delegates DOS to the resident TP runtime via far-calls; 314 far-rets present).
- **Disassembles to coherent Turbo Pascal game logic.** Hot region 0x300+ shows the classic
  TP calling pattern: push byte/word args → push `ss:`local and `cs:`const far-pointers →
  `lcall seg:off` to engine routines. Repeated `lcall 0xAF8:0xB0B` / `lcall 0x709:0x626` =
  the text/UI draw routines. CS-relative pointers index INTO the decoded string table, so
  **call sites cross-reference to the exact strings they print** — the key to mapping the engine.
- Comprehension wall = DOWN (x86 reads cleanly; START.EXE entry = self-relocator, understood).

### 5a. Structural map (Opus 4.8 push-through, 2026-06-12)
- **675 Pascal functions** in GAME.OVR — every `55 89 E5` (push bp; mov bp,sp) prologue.
  NB: this compiler emits `89 E5`, NOT `8B EC` (why a naive prologue scan returns zero).
- **Near-call graph (E8 rel16, fixup-free)** ranks usage. Hottest:
  `0x2B04A` 140 callers (228B frame, the workhorse) · `0x278DB` 33 (40-byte field copy =
  menu/label setup) · `0x0C7F2` 22 · `0x2ED72` 21 · `0x04636` 9 (776B frame = screen builder).
- **Library segment hierarchy (far-call targets):** `seg 0xAF8` = 1792 calls (core runtime:
  string/memory/UI; the 40-byte copy lives at `0xAF8:0xB25`), then `0xBA` 515, `0xB0` 311,
  `0x709` 264, `0x2B` 208. Game logic (overlay) → these resident library segments.
- **Architecture confirmed:** overlay = pure game logic (only 2 int10h, 3 int16h, no direct
  video writes); low-level video/IO lives in START.EXE (resident), reached via far-call.

### 5c. Overlay segment map — SOLVED (Fable 5, 2026-06-12)
TP overlay descriptor (in START.EXE, one per overlaid unit):
```
CD 3F            INT 3Fh (overlay-manager trap)
WORD = 0         not-loaded marker
DWORD            file offset of unit code in GAME.OVR
WORD             code size
WORD             fixup table size
WORD             entry-point count   (== # of CD 3F entry stubs that follow)
```
- **34 overlay units** tile 96% of GAME.OVR (197,451 / 206,105 bytes); layout per unit =
  `[code][fixup table]`. Map in `analysis/overlay_segmap.json`.
- **404 public entry points**; **673/675 functions assigned to units** (`analysis/unit_ledger.json`).
- Biggest units (the cores): stub-seg **0x38** (14.5KB, 117 entries) · **0x86** (14.3KB, 64) ·
  **0x25** (25) · **0x5E** (25) · **0x9E** (23) · **0x3C6** (20).
- **Far-call resolution:** START.EXE has 0 relocations (self-relocates), so resident
  `seg:off → START.EXE file 0x200 + seg*16 + off`. Validated: **`seg 0xAF8` = Turbo Pascal
  SYSTEM runtime** (software FP at `:0xB25`, `Val` string→number at `:0xDC0`) — its 1792 calls
  are language runtime, NOT game logic (discount them when analyzing). Game-specific resident
  helpers = segs `0xBA`, `0xB0`, `0x709`.
- **858 Pascal strings** recovered with offsets (`analysis/label_units.py`). Keyword sweep
  confirms all systems present: combat / magic / character / town / items / dungeon / menu.

### 5d. REMAINING = per-unit labeling campaign (parallelizable)
With the segment map done, label each of the 34 units' game role by disassembling its entry
points + following non-runtime calls + string xrefs. This is the fan-out task — one agent per
unit. Then system specs (combat, magic, dungeon, ECL VM) + redevelopment. See `HANDOFF_for_fable.md`.

## Remaining tiers
1. Full GAME.OVR routine ledger (label the hot draw/print/combat routines via string xrefs).
2. ECL bytecode VM — opcode table + interpreter (ground truth = in-game events).
3. GEO ground-truth confirmation vs Cluebook maps; crack the 8X8D wall-tile format.
4. Redevelopment: GEO + tiles + sprites → walkable level in a custom interface or Unreal.

## GEO cell format + 3-D wall rendering (fully decoded — see docs/WALL_RENDER_DECODED.md)
Each 16×16 GEO cell = 4 planes: plane0 N/E wall nibbles, plane1 S/W wall nibbles, **plane2 =
per-cell backdrop/texture id** (0x00 open street, 0x8x building variants, 0x0B alt ground),
**plane3 = feature flags** (bits 0/2/4/6 = N/E/S/W interactive). The **wall nibble value (1-15)
is the wall TYPE** from a finite set: doors = 5/10/11/13/15 (70-95% plane3-flagged), arches =
2/3/8, plain stone = 1/4/9/12/14. **8X8D{1..8}.DAX = 8×8 tile sets** (70/31/45 tiles; tile 17 =
masonry stone); **WALLDEF{1..8}.DAX = wall-face tile-grid tables** (40/39 row markers) that
compose the faces; **BACPAC.DAX = wilderness terrain tiles** (not the city backdrop). The
reproduction renders this faithfully (textured walls/cobble street, data-driven doors on front
+ side walls, AREA-map door markers, passable doors). Interface logic in docs/MANUAL_DECODED.md.

## Reusable kit
The DAX container parser + RLE codec are game-agnostic for the Gold Box family and are
factored into `kit/dax.py` for reuse on the other 11 titles.

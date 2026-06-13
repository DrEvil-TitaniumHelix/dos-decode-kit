# How we did this — full tools, assets, skills & methods

Paste-ready for the video description / Reddit "tech appendix." Everything below was actually
used to decode Pool of Radiance (1988) and build the playable reconstruction. Honest about what
each thing did.

## TL;DR stack
Claude Fable 5 + Claude Opus 4.8, orchestrated in Claude Code via a multi-agent workflow ·
Python 3.13 + capstone (x86-16 disassembly) + Pillow (render-to-validate) · ffmpeg + Chrome
DevTools Protocol for capture · HTML5 Canvas for the playable build ·
ground-truthed against the original 1988 manuals.

## Models & orchestration
- **Claude Opus 4.8** — carried most of the load: planning, scaffolding, a lot of the decode grind,
  data-structure work, and the reconstruction. The workhorse that got us most of the way.
- **Claude Fable 5** (Mythos-class) — when Opus hit a wall on the hardest cracks, Fable broke through,
  did the decode, and carried on. ⚠️ **No longer available — decommissioned 2026-06-12** (US export-control
  directive). The "escalate to Fable at the wall" step isn't reproducible today; whether the method still
  completes on Opus alone is the open question this kit puts to you.
- **Model-aware routing** — Opus carries it; escalate to the higher-capability tier only at the walls.
  *The right tool for each layer, not one model for everything.*
- **Claude Code** — the agent harness everything ran in (tools: shell, file edit, web, subagents).
- **Multi-agent Workflow** — the ECL bytecode-VM decode ran as a 10-agent workflow (locate
  interpreter → decode 41 opcodes in parallel → crack the text codec → synthesize), ~918K tokens.

## Reverse-engineering stack
- **Python 3.13.7** — all analysis scripting.
- **capstone 5.0.7** (`CS_ARCH_X86, CS_MODE_16`) — 16-bit x86 disassembly of `GAME.OVR`/`START.EXE`.
- **Custom tooling (in `analysis/` + `kit/`):**
  - `kit/dax.py` — the Gold Box DAX archive reader (container directory + RLE codec).
  - overlay segment-map parser — Turbo Pascal "FBOV" overlay → 34 units, 404 entry points.
  - function-prologue scorer — found 675 Pascal functions (`55 89 E5`) + the call graph.
  - `ecl_textcodec.py` — the cracked 6-bit ECL text codec (closed-form + engine-faithful forms).
  - bytecode analyzers — ECL header/opcode/operand structure.
- **Far-call resolution model** — `START.EXE` self-relocates (0 relocations), so resident
  `seg:off → file = 0x200 + seg*16 + off`; this made every helper call legible.

## Asset extraction & rendering
- **Pillow (PIL) 11.3** — sprite/map/texture decoding and the **render-to-validate** method
  (render at candidate settings, let the eye confirm). Also built the video cards + the money shot.
- **EGA 16-color palette** — the era's standard, recovered/applied to all graphics.

## Source material (inputs)
- **Original game files** — the shipped 1988 MS-DOS release.
- **Original binary:** `START.EXE` (loader) + `GAME.OVR` (Turbo Pascal overlay) + 100+ `.DAX`
  archives + `CHRDATA*.SAV/.ITM` (characters/items) + `ECL1-8.DAX` (the content bytecode).
- **Shipped 1988 manuals** (`Manual.pdf`, `Adventurers Journal.pdf`, `Cluebook.pdf`) — used as
  ground truth to validate every decoded structure.

## The playable reconstruction
- **HTML5 Canvas + JavaScript** — first-person dungeon renderer + tactical combat, runs in any browser.
- **`export_game.py` → `game_data.js`** — pipeline that turns the decoded data into the game's data.
- **`combat.js`** — AD&D 1e-style tactical combat (THAC0/AC/d20/weapon dice) on the real stats.
- 100% decoded inputs: 29 dungeon maps (GEO), characters (CHRDATA), items/treasure (ITEM .DAX),
  sprites (CBODY/CPIC), wall textures (8X8D), and **real encounter/dialog text (ECL, 6-bit codec)**.

## Video & capture pipeline
- **Chrome DevTools Protocol** (via Python `websockets`) — headless-drove the game's autoplay mode
  and captured frames.
- **ffmpeg** — assembled frames → mp4 gameplay clips.
- **Headless Chrome screenshots** — rendered the HTML overlay/title cards (transparent PNGs).
- **Node.js v22** (present in the toolchain).
- **DaVinci Resolve** — final edit/overlays (the same pipeline as the Midwinter video).

## The method (the actual "how")
1. Crack the container + compression codec first (one codec unlocked every asset; reads ~12 Gold Box games).
2. Render to validate — the eye is the oracle.
3. Manuals as ground truth.
4. Map the engine — function inventory + call graph + overlay segment map + far-call resolution.
5. Decode the content VM — find the interpreter, decode opcodes by side-effects, follow the print
   opcode to crack the text codec, recover the real game text.
6. Reconstruct — feed it all into a new front-end.
Full write-up: `METHODOLOGY.md` and `docs/ECL_VM_DECODED.md`.

## Honesty notes
- This is **reverse-engineering + reconstruction**, not "decompilation."
- **Clean-room** — no answers carried over from the first game (Midwinter); only the method.
- Every claim is tagged **verified** (byte/disasm-confirmed) vs **uncertain** (best-evidence
  inference). E.g., the text codec is verified bit-identical to the engine; some ECL operand
  grammar remains an open item (needs a small helper-segment emulator) and is flagged as such.
- No original game code or copyrighted data is redistributed — the kit ships the *method* + tools.

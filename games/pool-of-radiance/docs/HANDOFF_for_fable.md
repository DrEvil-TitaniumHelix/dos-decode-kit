# HANDOFF — Full Decode Campaign: Pool of Radiance / SSI Gold Box engine

**For:** Fable 5 (or a multi-agent Opus 4.8 workflow) running the full-coverage decode.
**From:** Opus 4.8 push-through, 2026-06-12. Everything below is byte-verified or call-graph-derived.
**Goal:** the Midwinter-grade deliverable — a labeled ledger of all 675 functions + a faithful
spec of the engine systems, so the game can be re-implemented (custom interface or Unreal).

## Why this is a handoff, not a dead end
Opus 4.8 already breached the comprehension wall: the x86 reads cleanly, and the structural
map (below) is done. What remains is **endurance + breadth** — labeling 675 functions and
resolving the overlay segment map — the kind of overnight multi-agent campaign that produced
the Midwinter 602/602 ledger. No mysterious-hex blocker is known to remain. If Fable 5 is
refused by the Mythos-tier safety gate and falls back to 4.8, a 4.8 multi-agent workflow can
run this same brief — the work is parallelizable by function range.

## Ground truth (use these to validate every claim)
- Manuals in the game dir: `Manual.pdf`, `Adventurers Journal.pdf` (journal entries by number),
  `Cluebook.pdf` (printed dungeon maps — the GEO validation oracle).
- 728 plaintext strings in GAME.OVR (length-prefixed Pascal strings from offset 0; ~5% of file).
- The DAX data files (already fully decoded — see below) constrain the data structures the code reads.

## What is already DONE (don't redo)
- **DAX container + RLE codec + EGA sprite format** — fully decoded & validated (1245/1245 blocks;
  113/113 archives). Reusable reader: `kit/dax.py`. Sprites confirmed by eye.
- **GAME.OVR = Turbo Pascal `FBOV` overlay, NOT packed** (entropy ~6.9). 675 functions
  (`55 89 E5` prologues). Near-call graph + library-segment histogram computed
  (`analysis/ledger.py`, `analysis/ovr_recon.py`).

## The campaign (suggested decomposition)
1. **Overlay/segment map FIRST.** Parse the FBOV structure + START.EXE relocations so far-call
   `seg:off` resolves to GAME.OVR/START.EXE file offsets. This unlocks every `lcall` target.
   Hot segments to label first: `0xAF8` (1792 calls — core string/mem/UI; e.g. `0xAF8:0xB25` =
   40-byte memcopy), `0xBA`, `0xB0`, `0x709`, `0x2B`.
2. **Label the hot core** (top-50 by caller count) via string xrefs + behavior. Anchors:
   `0x2B04A` (140 callers, the workhorse), `0x278DB` (menu/field setup), `0x04636` (776B screen builder).
3. **Fan out over the 675 functions by file-offset range** (parallel agents), each producing
   ledger rows: `{offset, callers, frame_size, calls_out, strings_xref, hypothesis, evidence}`.
4. **System specs** (Midwinter-doc style) for: character/combat data (`CHRDATA*`, `ITEMS`,
   `SAVGAMA.DAT`), the ECL script VM (`ECL1-8.DAX`), the GEO map renderer + 8X8D wall tiles.
5. **Cross-validate** vs manuals (combat tables, spell lists, dungeon maps).

## Still-open data-layer items (good warm-up tasks)
- **GEO maps:** confirm grid size (32×32×1B vs 16×16×4B) + nibble assignment vs a Cluebook map.
- **8X8D wall tiles:** format uncracked at width=8 (try EGA planar / alternate sheet width).
- **ECL1-8.DAX:** the event/dialog bytecode VM — opcode table + interpreter.

## Files
- Workspace: `.\`
- Findings: `games/pool-of-radiance/docs/FINDINGS_pool_of_radiance.md`
- Analysis scripts: `games/pool-of-radiance/analysis/*.py`
- Reusable kit: `kit/dax.py`
- Game files: `games/pool-of-radiance/extracted/poolrad/` (START.EXE, GAME.OVR, *.DAX, manuals)

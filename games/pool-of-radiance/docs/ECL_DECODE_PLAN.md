# ECL VM decode plan — the blocker to a complete game

The ECL (Event Control Language) bytecode in `ECL1-8.DAX` is the game's content engine:
every encounter, NPC line, room event, quest branch, monster placement, treasure, and win
condition. Decoding it = turning the engine shell into the actual Pool of Radiance.

## What's known (2026-06-12 investigation)
- **Interpreter = Turbo Pascal `CASE` dispatch**, ~40 opcodes. NOT a simple `jmp [table*2]`
  (TP compiles dense CASE through a runtime helper) — so a jump-table scan of GAME.OVR finds
  nothing; the dispatcher must be found via the TP case-jump pattern or by tracing ECL-buffer reads.
- **Text is COMPRESSED**, not enciphered. mask-0x7F, XOR(1..127), ADD/SUB(1..127) over all ECL
  data all fail to surface English. The decompressor lives inside the VM (a "print" opcode).
- **Bytecode structure (legible):** each ECL block = a header of `WORD val, 01, type` records
  (event offset table) + bytecode. Bytecode references **game-state addresses directly**
  (e.g. `D2 6D`/`D3 6D` = vars at 0x6DD2/0x6DD3 — area flags). Byte 0x01 is the most common
  token (726×), 0x00 next, then 0x80/0x05/0x03/0x6E.
- ECL ids match GEO ids per area (ECL1 ids 18,24 = GEO1 maps 18,24): one ECL program per area.

## The campaign (multi-agent workflow — the realistic path)
1. **Find the dispatcher.** Trace where ECL data (loaded via the DAX loader) is read with a
   program-counter; the byte-read + TP-case is the VM loop. Candidate region: the big units
   (0x6C 17.5KB, 0x38 core). Look for the TP case-helper far-call after an opcode fetch.
2. **Decode the 40 opcodes** (parallel, one agent per handler): print-text, start-combat,
   give-item, set/test-flag, conditional-jump, move-NPC, end. Each handler's far-calls
   (resolved via the segment map) reveal its action.
3. **Crack the text codec** — once the print opcode is found, its read loop reveals the
   compression (likely a dictionary or bit-packed charset). This unlocks ALL dialog/room text.
4. **Interpret the scripts** — run/transcribe ECL1-8 into human-readable area scripts
   (encounters + text + branches), cross-validate vs the Cluebook walkthrough.
5. **Wire into the reproduction** — real encounters, dialog, and quests per area.

## Realistic effort
Comparable to the entire rest of the 2026-06-12 decode combined. Solo = slow; the Midwinter-
style multi-agent overnight run is the right tool. Trigger: the author says "use a workflow".

## Everything else for a complete game is ALREADY decoded
maps (29 levels), walls (textured), sprites, monsters, characters, items, treasure (110),
combat math, class groups. The ECL is the one remaining frontier.

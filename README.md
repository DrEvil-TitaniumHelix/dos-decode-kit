# The DOS Decode Kit

A repeatable method — and the actual tools — for **reverse-engineering and reconstructing old DOS
games**: crack the container, decode the assets and data, map the engine, recover the content, and
rebuild the game in a modern, editable front-end.

## Proven, end-to-end, on two very different games
- **Midwinter (1989)** — decoded the **entire codebase**, 602 functions mapped and labeled, **including
  its 3D world** (the terrain generator was replicated and its output matches the original bit-for-bit).
- **Pool of Radiance (1988)** — taken **end-to-end, from binary decode to a playable reconstruction**:
  container + compression codec, 400+ sprites, 29 dungeon maps, character/item data, wall textures, and
  the ECL content bytecode (a 41-opcode VM + 6-bit text codec) — rebuilt into a playable game.

Two completely different engines (a 3D action-strategy game and a Turbo-Pascal D&D RPG), same method.

## How it works
The full pipeline is in **[`METHODOLOGY.md`](METHODOLOGY.md)**: unwrap → container/codec → assets
(render-to-validate) → data structures (manuals as ground truth) → engine map → content VM → reconstruct.
Per-game findings and the decode write-ups are in `games/<game>/docs/`, and the tools that did the work
are in `games/<game>/analysis/` and `kit/`.

## ⭐ A note on the models — and a challenge to you
This was driven through Claude Code with **model-aware routing**:
- **Claude Opus 4.8** carried most of the load — planning, the decode grind, reconstruction.
- **Claude Fable 5** broke through on the hardest cracks when Opus hit a wall.

**Fable 5 was decommissioned on 2026-06-12** (US export-control directive), so the "escalate to Fable at
the wall" step isn't reproducible today. **Opus 4.8 and the open tier remain available.** The open
question — and the point of releasing this — is: **how much of it can you reproduce on Opus alone?** Pull
the kit, point it at a game, and find out. (I'm about to find out too — next subject: *Curse of the Azure
Bonds*.)

## ⚠️ Bring your own game files
This repo ships the **method and the tools only**. It does **not** include any original game binaries,
decoded game data, sprites, box art, or manuals — that material is copyrighted. The decode/extract scripts
run against **your own legally-obtained copy** of a game and regenerate the data locally
(e.g. `game_data.js`, `ui_art.js` are produced by `analysis/export_game.py` + `analysis/make_ui_art.py`
and are intentionally git-ignored).

## Honesty
- This is **reverse-engineering + reconstruction**, not "decompilation."
- **Clean-room across games** — no answers were carried from one game to the next, only the method.
- Findings are tagged **verified** (byte/disasm-confirmed) vs **uncertain** (best-evidence inference).
- No original game code or copyrighted data is redistributed.

## Exhibit A
The Midwinter decode (the first proof) is its own repo: **github.com/DrEvil-TitaniumHelix/midwinter-decode**.

## License
MIT (tools + docs). Original games remain the property of their respective rights holders.

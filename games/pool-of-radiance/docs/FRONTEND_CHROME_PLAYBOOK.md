# Front-end chrome playbook — how the faithful recreation got crisp (2026-06-12)

Status: **DONE and approved by the author.** This documents how it was done so any session/model
(Opus, Fable, anyone) can maintain or extend it. This is pure web front-end work — no binary
analysis, no RE tooling needed or allowed (see FABLE_BUILD_JOB.md for the original job + its
hard boundaries, which still apply to follow-on work).

## The three fixes, and exactly where they live

### 1. Crisp rendering (kill the upscale haze)
`reproduction/faithful.html`:
- Canvas element is `width=960 height=600` (3× integer of the logical 320×200), CSS is
  `width:960px;height:600px` — backing store == display size, so the browser never resamples.
- One `cx.scale(3,3)` right after getContext; **all drawing code stays in 320×200 coordinates.**
- `imageSmoothingEnabled=false` so decoded art (title, portraits, sprites) upscales
  nearest-neighbor.
- Rule: never draw text with `fillText` (it anti-aliases and smears at any scale). Never pick a
  non-integer scale factor (the old 800×600 was 2.5×/3.0× — that was the haze).

### 2. Woven rope border + gold ornaments
- Generator: `analysis/make_ui_art.py` (Python+Pillow, original art — reads NO game files).
  It emits `reproduction/ui_art.js` = `UI_ART` object with **palette-indexed pixel arrays**
  (not data-URL images — arrays build synchronously, no Image.onload race in headless capture).
- Rope look: the trick that makes it read as rope instead of candy-cane stripes is the
  per-row CURVE table (`[3,1,0,0,0,1,3]`) which bends each diagonal strand into a `)` lobe.
  Stripe cross-section `[K,K,R,L,L,R,R,R]` = gap, body, highlight, body. Tile 8×7, EGA-only
  colors (#AA0000, #FF5555, gold #FFFF55, brown bevel #AA5500).
- In faithful.html: `buildTile()` converts arrays → offscreen canvases; `rope(x0,y0,x1,y1)`
  tiles bands (clipped, so any length works) and stamps 9×9 gold ornaments at corners + spaced
  ~110px along edges; `ropeHBand`/`ropeVBand`/`orn` are the primitives. The full-width message
  divider is a bare `ropeHBand` + ornaments.
- To change the art: edit make_ui_art.py, run it (regenerates `_ui_art_proof.png` to eyeball
  + `ui_art.js`), reload. Never hand-edit ui_art.js.

### 3. Blocky bitmap font
- Authored as a 5×7 caps font (hex rows in `FONT57` in make_ui_art.py), then **bolded to 2px
  strokes via `(r<<1)|r`** → 6×7 glyphs, 8px advance (40 cols across 320px, like the real game).
- `text(x,y,s,col)` in faithful.html draws glyph pixels with 1×1 `fillRect` at integer logical
  coords → 3×3 device pixels, zero anti-aliasing. Uppercases input; unknown chars skipped.
  Glyph set: A-Z 0-9 `.,:'-!?/()&<>` space. Add glyphs in FONT57 + rerun the generator.
- `wrap(s,n)` word-wraps message text to 37 cols, 2 lines shown.

## Layout constants (320×200 logical space)
- Outer rope frame `rope(0,0,320,190)`; command line BELOW it at y=192 (magenta), like the
  original. Viewport frame `rope(8,8,148,148)`, interior 124×124. Roster: icons x=154,
  names x=167 (8-char first name + 3-char class), AC x=268, HP x=294, rows 12px from y=24.
  Status line right column y=138. Message divider band at y=150, text rows y=160/170 at x=10.

## Capture / verification loop (how to judge changes)
- Headless Chrome, **absolute** screenshot path (relative = silent Access-denied failure):
  `chrome --headless --disable-gpu --force-device-scale-factor=1 --window-size=980,660
  --screenshot=<ABS>.png "file:///...faithful.html?notitle"`
- Query hooks: `?notitle` (skip title), `?fight=1` (boot into combat), `?autoplay=1` (demo
  for video capture).
- Judge with a side-by-side vs `video-assets/artifacts/MS-DOS_Shot_Gameplay.png`, never by
  self-assessment. Composer one-liner used: crop canvas (10,10,970,610) → NEAREST down to
  320×200 → NEAREST up to 640×400 → paste next to the reference (`_side_by_side.png`).

## Known/accepted quirks
- Title screen edge garbage + 320×201 height: that's in the decoded asset itself — do not
  "fix", the data is ground truth.
- "PROCEDE" etc. in ECL text: original game's spelling. Leave it.
- Font is an era-appropriate original, NOT SSI's exact bitmap (their font remains undecoded —
  that would be RE work, out of scope here).

# Pool of Radiance — Interface Logic (decoded from the manual + binary)

Like the Midwinter "Book of Ice": the manual is ground truth for the game's *logic*; this doc
captures the menu/interface system so the recreation can reproduce it and so the matching code
can be found in GAME.OVR.

## Setting: it's a CITY, not a dungeon
Most adventures are in **New Phlan**, a ruined city, played in **blocks of 16×16 squares**
(matches the decoded GEO 16×16 cell format). The party moves block-to-block via long low-ceiling
corridors. Open squares = plaza/street; that is why the Podol Plaza block has a big open center.
"Civilized" Phlan has Shops, Inns, Taverns, Training Hall, City Council, Docks, Temples.
Travel modes: **Town** (3-D first-person) and **Wilderness** (overhead, 8-direction).

## Per-cell texture set (the author's hint — confirmed in the data)
Each GEO cell carries 4 planes: plane0 = N/E wall nibbles, plane1 = S/W wall nibbles,
**plane2 = backdrop/texture id**, plane3 = feature/event flags. plane2 is a *finite set*:
`0x00` = open floor (plaza/street), `0x8x` (0x84-0x8A) = building-wall backdrop variants,
`0x0B` = alternate ground. In Podol Plaza (#18) the 0x00 cells form the open center, ringed by
0x8x building backdrops — i.e. each map point has a well-defined texture, exactly as the author said.
This is what drives the finite wall/floor/ceiling/open-area texture selection.

## Menu tree (verbatim from the manual)
```
ADVENTURE MENU   : MOVE  VIEW  CAST  AREA  ENCAMP  SEARCH  LOOK
  MOVE   -> 3-D travel: forward/back enters a square (1 min game-time); turn L/R (free).
            SEARCH on => 10 min/square. Wilderness => 8-direction, ½ day/square.
  VIEW   -> Character Screen (see below) for the active character.
  CAST   -> Cast Menu: active character throws a memorized spell.
  AREA   -> overhead map of the block around the party (unavailable if lost).
  ENCAMP -> Encamp Menu.
  SEARCH -> toggle Search Mode (slow move, finds secret doors/traps).
  LOOK   -> examine the current square.

ENCAMP MENU      : SAVE  VIEW  MAGIC  REST  ALTER  EXIT
  SAVE  -> save game.   VIEW -> character screen.   MAGIC -> memorize/rest spells.
  REST  -> pass time to heal HP & regain spells (interruptible by encounters).
  ALTER -> party order / combat icons / drop.   EXIT -> back to Adventure Menu.

VIEW (Character Screen) MENU : ITEMS  SPELLS  TRADE  DROP  EXIT
  ITEMS  -> Item Menu: READY USE TRADE DROP HALVE JOIN SELL ID EXIT
  SPELLS -> memorized/known spells (casters only).

COMBAT (reference) : MOVE  AIM  …  (AIM uses manual/quick/target sub-modes)
SHOP   : BUY VIEW SELL … ;  TEMPLE : HEAL VIEW TAKE POOL SHARE APPRAISE EXIT
"Exit"/Escape on any menu returns to the next-higher menu.
```

## Character Screen fields (from CHRDATA decode + manual)
name, race/class, level; six abilities STR/INT/WIS/DEX/CON/CHA (+ exceptional STR for fighters);
AC, current/max HP, THAC0; status (OK / Unconscious / Dying / Dead / Fled / Gone); XP;
carried items with Ready flag; memorized spells. All of name/abilities/exSTR/HP/thief-skills/
items are decoded from CHRDATA*.SAV/.ITM; class group from off 284.

## Combat statuses
OK, Unconscious (0 HP, stable), Dying (<0, bandage or die), Dead (raise w/ CON check),
Fled (rejoins after), Gone (destroyed, unraisable).

## Where this maps in GAME.OVR (for the redevelopment)
- Adventure-menu dispatch + 3-D view = the **TextWindowPaint / GfxBlit** units (0x6c text/format,
  0x3b0 blitter) + the ECL `DISPLAY_WINDOW`/`MENU_SELECT` opcodes (0x11/0x12/0x15).
- VIEW/character screen = **CharacterState** unit 0x38 (the party/char record core, 117 entries).
- AREA overhead = reads the GEO block planes; ENCAMP/REST = time + HP/spell regen logic.

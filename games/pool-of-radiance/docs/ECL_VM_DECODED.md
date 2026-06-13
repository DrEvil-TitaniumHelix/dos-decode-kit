# Pool of Radiance — ECL (Event Control Language) Bytecode VM

**Reverse-engineered specification.** Pool of Radiance (SSI, 1988), MS-DOS, Gold Box engine.
Target binary: `extracted/poolrad/GAME.OVR` (Turbo Pascal "FBOV" overlay, 206 105 bytes, 675
Pascal functions). Content data: `ECL1.DAX` … `ECL8.DAX` (DAX-compressed event blocks).

Every address below is a **file offset into GAME.OVR** unless noted. Every claim is tagged
**VERIFIED** (byte- or disasm-confirmed with capstone `CS_MODE_16`, or reproduced on real ECL
data) or **UNCERTAIN** (best-evidence inference, helper-driven semantics not statically
executable). Tooling used: Python + capstone 5.0.7, the DAX reader `kit/dax.py`, and the text
codec `analysis/ecl_textcodec.py`.

---

## 1. Interpreter location and dispatch mechanism — VERIFIED

The ECL VM is a classic fetch–decode–dispatch loop driving a stack of loaded ECL bytecode blocks.

### 1.1 Global VM state (GAME.OVR data segment)

| Address  | Meaning |
|----------|---------|
| `[0x49ED]` | **PC** — current byte offset into the active bytecode block |
| `[0x49DE]` | **buffer far-pointer** (seg:off) of the active bytecode block in memory |
| `[0x6F7F]` | **current opcode** byte (latched each fetch); `[0x6F7E]` = previous opcode |
| `[0x442E]`, `[0x49FF]` | **stop flags** — loop exits when either is non-zero |
| `[0x6F70]` | head of the **call/GOSUB stack** linked list (6-byte nodes) |
| `[0x6F78]..[0x6F7D]` | **6-byte comparison-result flag bank** (set by compare ops, tested by the IF family) |
| `[0x49D2]`, `[0x49D6]` | **area-struct far-pointers** (encounter state, loop counters, max-explored coord) |
| `[0x7045/0x7085]`, `[0x7046/0x7086]`, `[0x7047/0x7087]`, `[0x7048/0x7088]` | resolved **operand slot** lo/hi byte arrays (operands 0..3) |
| `[0x7006]/[0x7007]` | **operand type tags** — high bit `0x80` = string operand, else numeric |

### 1.2 Fetch–decode loop @ `0x03EB7` — VERIFIED

```
mov ax,[0x49ED]          ; PC
les di,[0x49DE]          ; buffer far-ptr
add di,ax                ; di = bufbase + PC
mov al,es:[di+0x6700]    ; fetch opcode byte  (+0x6700 = ES-relative load bias)
mov [0x6F7F],al          ; latch current opcode
push cs
call 0x3C73              ; dispatch
jmp  0x3EC5              ; loop (until stop flag set)
```

The loop fetches **only the opcode byte**; it does **not** advance PC over operands. Each handler
pulls its own operands through the resident operand-fetch helpers (below), which advance `[0x49ED]`.

### 1.3 Dispatch @ `0x03C73` — VERIFIED

Not a jump table. Turbo Pascal compiled the `CASE` as a dense `cmp al,n / push cs / call handler /
jmp end` cmp-chain over `[0x6F7F]`, covering `al = 0x00..0x3D` contiguously. **`0x1F` is the only
gap** (no case → no handler). A naive jump-table scan therefore finds nothing — this was the
original red herring.

### 1.4 Operand-fetch helpers (resident, far-called via `lcall 0x2B:xx`) — VERIFIED call sites

| Helper | Role | Sites |
|--------|------|-------|
| `2B:2A` | declare/prefetch N operands for this instruction | 42 |
| `2B:25` | read next inline byte & advance PC | 52 |
| `2B:4D` | resolve operand slot (hi:lo pair) → far value/address in AX | many |
| `2B:52` | store a value to a resolved destination address | 35 |
| `2B:5C` | store a string/struct to a resolved destination | — |
| `2B:8E` | **skip the following statement** (used only by the IF family, exactly 6 sites) | 6 |
| `2B:75` | stream skip-to-label / branch-target select | 2 |

> **Operand byte-grammar — RESOLVED 2026-06-12 (was the single biggest open item).**
> The wire format was read straight off the bytecode (no `0x2B` emulation needed). Every operand
> is a **tagged value**:
>
> | Tag | Form | Meaning |
> |-----|------|---------|
> | `0x00` | `00 BB` | immediate byte `BB` |
> | `0x01` | `01 LO HI` | WORD (little-endian) — variable reference **or** word immediate `0xHILO` |
> | `0x80+` | `tag …` | string/struct selector (high-bit family; PRINT/MENU text path) |
>
> Each opcode pulls its **fixed** operand count (the §2 table) of these tagged values; that is all
> the resident `2B:2A/2B:25/2B:4D` helpers were doing — fetch-and-advance over the tag grammar.
> Worked example: `09 00 02 01 D2 6D` = `SET_VAR #2, $6DD2` (var 0x6DD2 := 2). *(The earlier note
> read the trailing `10` of the next instruction as a PRINT opcode — it is the immediate value
> `0x10`, not an opcode.)*
>
> **GOTO/label addressing:** labels live in a logical space; file offset = `label − 0x98F1`
> (fit empirically, lands 13/13 observed targets on valid opcode bytes; clean targets hit exact
> instruction boundaries). `GOTO_LABEL`/`GOTO_SELECT` (0x25/0x26) carry an **inline jump table**:
> `op0 + count(byte) + count×word` entries.
>
> Disassembler: **`analysis/ecl_disasm.py`** (static, no emulation). Full ECL1 #18 Podol Plaza
> listing: `analysis/_ecl_ECL1_18.asm`. The same grammar disassembles other blocks cleanly
> (verified on ECL3 #0). Remaining fuzz: the `0x80+` string-operand widths and a ~3-byte skew on
> jump-table entry points are not byte-perfect, but control flow is now statically readable.

---

## 2. Opcode table (41 opcodes, 0x00–0x3D; 0x1F unused)

Handler addresses and dispatch grouping are **VERIFIED** from the `0x03C73` cmp-chain. Semantics
confidence is per-row. "Operands" = the count declared via `2B:2A` plus the inline bytes the
handler reads.

| Code | Name | Action (summary) | Operands | Handler | Conf | Key evidence |
|------|------|------------------|----------|---------|------|--------------|
| 0x00 | STOP / END | Terminate event: set stop flag `[0x442E]=1`, inc PC, free call-stack list `[0x6F70]`, redraw frames | none | 0x0D47 | 0.95 | `mov byte[0x442E],1` then list-free loop |
| 0x01 | GOTO | Unconditional jump: resolve op0 → write `[0x49ED]` | 1 | 0x0E3A | 0.95 | `lcall 2B:4D; mov [0x49ED],ax` |
| 0x02 | CONTROL1 | Single-operand control op via helper `2B:75` (branch/select family) | 1 | 0x0E57 | 0.50 | `push 1; lcall 2B:75` |
| 0x03 | CMP_OR_ASSIGN | Type-dispatched 2-operand compare/assign; string path vs numeric path on tag `0x80` | 2 | 0x0E6C | 0.70 | `cmp byte[0x7006],0x80` branch |
| 0x04 | ADD | dest = src1 + src2 (shared handler, selected by `[0x6F7F]`) | 3 | 0x0EE9 | 0.90 | `cmp al,4; add` then `lcall 2B:52` |
| 0x05 | SUB | dest = src2 − src1 | 3 | 0x0EE9 | 0.90 | `cmp al,5; sub` |
| 0x06 | DIV | dest = src1 / src2 (unsigned) | 3 | 0x0EE9 | 0.90 | `cmp al,6; div word` |
| 0x07 | MUL | dest = src1 * src2 (unsigned) | 3 | 0x0EE9 | 0.90 | `cmp al,7; mul word` |
| 0x08 | RANDOM | dest := bounded/random value (TP runtime math over a bound) | op0 dest + 1 inline bound | 0x0F7A | 0.60 | `lcall 0xAF8:0x11C0/119A/119E` then store |
| 0x09 | SET_VAR | Assign value into a variable/buffer; scalar (inline byte) or string (buf `0x70C8`) on tag `0x80` | op0 dest + value | 0x0FD8 | 0.65 | `cmp byte[0x7006],0x80` scalar/str split |
| 0x0A | MOVE_PARTY | Teleport party N nodes along the map-link list & redraw viewport | 1 inline byte (bit7=cmp-target flag, bits0-6=step count) | 0x1026 | 0.70 | walks `+0x104/+0x106`, `lcall 0xBA:0x767` redraw |
| 0x0B | ADD_NPC | Append area NPC/entity records (name strings, id byte), cap 63 | strA, strB, count, id | 0x1196 | 0.60 | `cmp [0x4435],0x3F/jb`, node link `+0x104`, name copy |
| 0x0C | LOOP_INIT | Init count-controlled loop; rolls a count into struct field `+0x582` | 3 inline bytes | 0x10FA | 0.55 | `lcall 0xBA:0x3E` roll, clamp `+0x582` |
| 0x0D | LOOP_NEXT | Loop back-edge: if `+0x582>0` decrement, re-issue body, inc PC | none | 0x155D | 0.60 | `dec es:[di+0x582]`, `inc [0x49ED]` |
| 0x0E | START_COMBAT | Trigger combat/fixed-monster fight; draw encounter frame, spawn or resume monster group | 1 inline byte (selector; 0xFF=none) | 0x159C | 0.60 | flags `[0x84C9]=1/[0x84E0]=1`, spawn `lcall 0x3D0:0x25` |
| 0x0F | SHOW_PICTURE | Load & blit a picture (8000-byte quarter-screen) into video seg 0xBA00 | op0 = picture id var | 0x1697 | 0.55 | `lcall 0x709:0xB66` → `mov ax,0xBA00; 0x1F40` blit |
| 0x10 | PRINT_TEXT | Decode & render a 40-col text string (the print path) | op0 = string ref | 0x16DA | 0.50 | width `0x28`(40), `lcall 0x709:0x9E3`; codec via §3 |
| 0x10* | INPUT_STRING | (same handler, input variant) read a typed line into buffer, store to var | op0 = dest var | 0x16DA | 0.60 | FillChar 0x28, `lcall 2B:5C` store |
| 0x11 | DISPLAY_WINDOW | Open/draw a text window/prompt panel (geom 0,0x0A,0x16,0x26) | conditional 1 byte | 0x174F | 0.55 | `cmp [0x6F7F],0x11`, `lcall 0x709:0x768` |
| 0x12 | DISPLAY_WINDOW_VARIANT | Same primitive as 0x11, sets active-window state `[0x5E24]=1/[0x5E25]=0x11`, arg=1 | as 0x11 | 0x174F | 0.50 | else-branch of 0x11 test |
| 0x13 | RETURN | Pop call-stack node `[0x6F70]`, restore PC + buffer, FreeMem 6 | none | 0x17E5 | 0.85 | restore `[0x49ED]` from node word0, FreeMem 6 |
| 0x14 | COMPARE_SET_FLAGS | Zero `[0x6F78..0x6F7D]`, read 4 operand words, compare; set EQUAL `[0x6F78]` or NOT-EQUAL `[0x6F79]` | 4 | 0x1833 | 0.75 | FillChar 6 @0x6F78; `cmp` → set flag |
| 0x15 | MENU_SELECT | Present selectable list, capture choice (ASK/CHOOSE) | ≥1 | 0x1C4E | 0.55 | walk list `+0x2A/+0x2C`, render rows |
| 0x16 | IF_EQUAL | Skip next stmt unless EQUAL flag `[0x6F78]` set | none | 0x1898 | 0.80 | `cmp al,0x16; cmp [0x6F78],0; lcall 2B:8E` |
| 0x17 | IF_NOT_EQUAL | Skip next stmt unless NOT-EQUAL flag `[0x6F79]` set | none | 0x1898 | 0.80 | dispatch `0x3D53 je → 0x1898`; tests `[0x6F79]` |
| 0x18 | IF_COND2 | Skip next stmt unless flag `[0x6F7A]` set | none | 0x1898 | 0.88 | `cmp al,0x18; cmp [0x6F7A],0` |
| 0x19 | IF_COND3 | Skip next stmt unless flag `[0x6F7B]` set | none | 0x1898 | 0.88 | `cmp al,0x19; cmp [0x6F7B],0` |
| 0x1A | IF_COND4 | Skip next stmt unless flag `[0x6F7C]` set | none | 0x1898 | 0.88 | `cmp al,0x1A; cmp [0x6F7C],0` |
| 0x1B | IF_COND5 | Skip next stmt unless flag `[0x6F7D]` set | none | 0x1898 | 0.88 | `cmp al,0x1B; cmp [0x6F7D],0` |
| 0x1C | CLEAR_OBJECT_LIST | Dispose dynamic object/encounter list `[0x6810]` (FreeMem 0x3F nodes), reset roster | none | 0x1FA3 | 0.70 | list-free loop on `[0x6810]`, clear `[0x4435]` |
| 0x1D | PARTY_STAT_AGGREGATE | Weighted average over party char-records → store to a slot | 1 | 0x200C | 0.60 | walk `[0x5D96]`, weighted sum / 10, `2B:52` |
| 0x1E | PARTY_FIELD_SURVEY | min/max/sum/avg of a selectable char field across party | 1 selector + reads | 0x217B | 0.60 | selector `0x6BA7`→`+0x79`, `0x6C1B`→`+0x11C` |
| 0x1F | *(unused)* | No dispatch case — gap in the ladder | n/a | none | 0.90 | no `cmp al,0x1F` exists |
| 0x20 | CHAIN_TO_ECL | End script + load+run another `ECLn.DAX` (area transition) | 1 byte = ECL file number | 0x1917 | 0.90 | build `"ECL"+n+".DAX"`, `lcall 0x7C:0x57`, set `[0x442E]=1` |
| 0x21 | SET_AREA_ENCOUNTER | Place/configure a fixed encounter for the current tile | 3 bytes (0xFF=none, 0x7F=special) | 0x19BA | 0.60 | write `+0x18A`, `lcall 0x3D5:0x43/0x3E` |
| 0x22 | TEST_PARTY_CLASS | Test party class composition (class byte `+0x2F` == 4 / 0x0A) → 2 vars | 2 | 0x236F | 0.60 | walk `[0x5D96]`, two `2B:4D/2B:52` |
| 0x23 | RANDOM_PICK | Random value/direction within an operand range → var `0x6DCB` | 4 (range bounds) | 0x240F | 0.60 | two `lcall 0xB0:0x48` RNG(1,6), store `0x6DCB` |
| 0x24 | AREA_STEP_EVENT | Per-step/area-event dispatcher; update max-explored coord, print status numbers | none | 0x24E1 | 0.55 | dispatch `0x28/0x22/0x25:0x25`, `%d` templates |
| 0x25 | GOTO_LABEL | Jump to a labeled location: scan label tables (`[0x7045]` lo / `[0x7085]` hi), write PC | 2 (label id, count) | 0x263E | 0.85 | match → `2B:4D` → `mov [0x49ED],ax` |
| 0x26 | GOTO_SELECT | Variant of 0x25: matched label → `2B:75` skip-to-label (ON-value/multi-target) | 2 | 0x263E | 0.55 | `[0x6F7F]==0x26` alt branch |
| 0x27 | LOAD_RESOURCE_PIC | Load a graphics/resource record (8 slot ids + selector), open `.DAX` | 8 ids + 1 selector | 0x26F6 | 0.60 | `mov word[di+0x67F4]`, `lcall 0x802:0x716` |

*Full handler→opcode map (VERIFIED from the cmp-chain) is preserved in `analysis/` notes; the
chain also groups `0x04-0x07`→0x0EE9, `0x11-0x12`→0x174F, `0x16-0x1B`→0x1898, `0x25-0x26`→0x263E.*

> Confidence ≥0.80 rows are structurally proven (PC writes, stop flags, FreeMem sizes, flag-bank
> tests). Rows at 0.50–0.70 have a correctly identified handler and a strongly-evidenced action
> but the exact operand wiring depends on the un-emulated `0x2B` helper.

---

## 3. Text codec — VERIFIED (cracked & reproduced)

ECL strings are **6-bit packed**: 4 characters per 3 bytes, MSB-first, with a charset remap.
Each string is stored back-to-back in the bytecode block, self-delimited by a `0x00` code.

- **Char remap** (leaf @ GAME.OVR `0x7BA6`): code `c <= 0x1F` → ASCII `c + 0x40` (`0x01`→`A` …
  `0x1A`→`Z`, plus `@ [ \ ] ^ _`); codes `0x20..0x3F` pass through (space, `! " ' , . -`, digits,
  `: ; ?`). Code `0x00` = terminator.
- **Unpacker** (@ GAME.OVR `0x8626`, reached from PRINT_TEXT 0x10 → string-load `0x8426`): a
  phase-1..4 sliding-window state machine over the bytecode buffer (`es:[di+0x6700]`, PC `[0x49ED]`).

Closed form (bit-identical to the engine's rolling-window form, verified on real samples):

```python
def chmap(c):                       # GAME.OVR 0x7BA6
    return c + 0x40 if c <= 0x1F else c

def decode_string(buf, pos):        # closed form of GAME.OVR 0x8626
    out = []; i = pos
    while i + 2 < len(buf):
        b0, b1, b2 = buf[i], buf[i+1], buf[i+2]; i += 3
        for c in (b0 >> 2,
                  ((b0 & 3) << 4) | (b1 >> 4),
                  ((b1 & 0xF) << 2) | (b2 >> 6),
                  b2 & 0x3F):
            if c == 0:
                return bytes(out)   # 0x00 = terminator
            out.append(chmap(c))
    return bytes(out)
```

Reference implementation: `analysis/ecl_textcodec.py` (`decode_string`, `scan_strings`).
**Proof:** brute-forcing alignments over ECL1 block id 18 surfaces **92–98 coherent English
strings**; closed-form and engine rolling-window models produce identical bytes on samples
`0x013E / 0x0B5E / 0x0E18`. The recovered text matches the published game (the Podol Plaza auction,
the wand of Garwin, etc.), independently corroborating the codec against ground truth.

---

## 4. Worked interpretation — ECL1 area 18 (GEO map 18) MAIN block

ECL ids map to GEO map ids per area; ECL1 id 18 is a **Slums / Podol Plaza** map. The block is
`0x1996` bytes after DAX decompression.

### 4.1 Header — VERIFIED structure, partially-resolved semantics

Five 4-byte records `[WORD value, 0x01, 0x01]` (20 bytes), then the text+code body:

```
rec0: 88 13 01 01   value 0x1388
rec1: B9 99 01 01   value 0x99B9   (high bit set)  &0x7FFF = 0x19B9
rec2: B7 9A 01 01   value 0x9AB7   (high bit set)  &0x7FFF = 0x1AB7
rec3: 14 99 01 01   value 0x9914   (high bit set)  &0x7FFF = 0x1914
rec4: 60 99 01 01   value 0x9960   (high bit set)  &0x7FFF = 0x1960
```

**Correction to the prior hypothesis (VERIFIED across 9 blocks in ECL1/2/3):** `rec0 = 0x1388`
(= 5000) is a **constant magic/sentinel in every block**, *not* a per-block MAIN offset. Records
1–4 carry the high bit `0x8000` and encode the four per-area event-handler entry points, but their
`&0x7FFF` values are **not raw byte offsets** (several exceed the block length in other blocks,
e.g. id 24 → `0x363B` > `0x1DE8`). The precise entry-point resolution is performed by the same
`0x2B` helper that drives label/GOTO resolution and is **not statically reducible** — flagged
UNCERTAIN. What is certain: 5 header records, rec0 sentinel = 0x1388, recs 1-4 high-bit-flagged
event handlers.

### 4.2 Bytecode structure — VERIFIED idioms, UNCERTAIN full linearization

The body interleaves the packed-text pool (front, from ~`0x13E`) with operand/code data. The
recurring on-disk instruction idiom is clearly visible, e.g. from offset `0x14`:

```
... 09 00 02 01 D2 6D    09 00 10 01 D3 6D    03 01 4F C0 ...
    SET_VAR  →var 0x6DD2  PRINT  →var 0x6DD3  CMP/ASSIGN →0xC04F
```

`01 <lo> <hi>` = a WORD operand; `D2 6D` resolves to **variable `0x6DD2`** (the documented ECL
state var). The opcodes that appear in this block (PRINT_TEXT 0x10, START_COMBAT 0x0E, MENU_SELECT
0x15/WINDOW 0x11, COMPARE 0x14 + IF family 0x16–0x1B, GOTO 0x01 / GOTO_LABEL 0x25) match the
encounter logic below. **A fully linearized, byte-exact transcript is NOT produced here** because
operand widths are helper-determined (§1.4 caveat); fabricating one would be dishonest. Instead the
block's behavior is reconstructed from the **verified decoded strings** (the player-facing content
the PRINT/MENU opcodes emit), which is itself strong proof the VM and codec are understood.

### 4.3 Reconstructed MAIN event — pseudo-script (content VERIFIED, control-flow inferred)

The MAIN event for this map is the multi-stage **Podol Plaza auction** encounter. Strings are
verbatim-decoded (offset shown); the `print/menu/combat/if` framing is the inferred structure that
the opcode set above implements:

```
EVENT main(area=Slums/Podol Plaza, map 18):

  # --- Plaza approach (offset 0x13E ff.) ---
  print  "THE PLAZA AHEAD IS CROWDED WITH MONSTERS. HOW WILL YOU PROCEDE?"   ; 0x13E
  menu   [ "STRIDE BOLDLY FORWARD!"                  ; 0x172
           "DISGUISE PARTY AS MONSTERS."             ; 0x185
           "SNEAK, REMAINING UNSEEN" ]               ; 0x19C
        -> set choice var (≈ 0x6DD2)

  if choice == BOLD:
        print "THE MONSTERS STAND READY ..."          ; 0x4A1 / 0x4B5
        combat  <plaza monsters>                       ; opcode 0x0E
  if choice == DISGUISE:
        print "THEY CHECK OUT YOUR PARTY, ..."         ; 0x2BA
        ; reaction roll (RANDOM 0x08 / RANDOM_PICK 0x23)
        print one of:
            "THEY GRUMBLE AND MOVE ON."                ; 0x3BF
            "LAUGH TO THEMSELVES AND WALK ON."         ; 0x3FB
            "'WE'RE GONNA HAVE TA TEACH YOU A LESSON!'" -> combat   ; 0x665
  if choice == SNEAK:
        print "YOUR PARTY SLIPS PAST THEM."            ; 0x43C
        on failure: print "YOUR COVER IS BLOWN." -> combat          ; 0x587

  # --- The auction (offsets 0x9B6 .. 0xF3E) ---
  print  "THE AUCTIONEER CRIES 'CREATURES OF ALL AGES, WELCOME TO THIS
          AUCTION FOR AN ITEM BOTH MAGICAL AND POWERFUL!'"           ; 0x9B6
  print  "THE AUCTIONEER HAS EITHER A WAND OR STAFF."                ; 0xA11
  menu   [ "STAND AND LISTEN" / "MOVE IN CLOSER" / "LISTEN TO COMMENTS" ] ; 0xA4B..

  print  "THE BIDDING ESCALATES TO 5,000 GOLD PIECES -- HIGH BID FROM A
          MAN IN PLAIN CLOTHES, NEXT TO AN OGRE."                    ; 0xA8C
  menu   [ "WAIT FOR WINNER" / "TRY TO LEAVE" ]                      ; 0xAFE / 0xB0C

  print  "THE MAN THEN SPEAKS A WORD AND THE AUCTIONEER'S BLOCK IS
          ENVELOPED IN ... MASS CONFUSION. SUDDENLY, THE OGRE SPRINTS
          FROM THE DARKNESS."                                        ; 0xB5E / 0xBA7
  menu   [ "FOLLOW THE OGRE" / "MOVE QUIETLY AWAY"
           "LOOK FOR THE MAN IN PLAIN CLOTHES" ]                     ; 0xBEA..

  if follow_ogre:
        print "THE OGRE IS TACKLED AND SEARCHED. HE DOESN'T HAVE
               THE ITEM ON HIM."                                     ; 0xC32
  print  "'GARWIN, I'LL GET YOU!' CRIES THE AUCTIONEER. HOWEVER,
          THE MAN HAS ESCAPED IN THE CONFUSION."                     ; 0xCC2
  print  "YOU NOW SEE THE WAND ISN'T A MAJOR ARTIFACT, IT'S ONLY
          A WAND OF FEAR!"                                           ; 0xE18
  print  "THE AUCTION OVER, THE MONSTERS GRUMBLE AND TURN AWAY."     ; 0xF3E

  # --- Adjacent room events in same block ---
  on_enter_tavern:
        print "YOU HAVE ENTERED A CROWDED TAVERN."                   ; 0xFC0
        print "YOU OPENED THE DOOR INTO A DRUNK BUCCANEER."          ; 0xFEA
        print "'ONE OF YOU SHALL PAY FOR THIS INSULT...'"            ; 0x100F
        menu  "WHO WILL CHALLENGE THE BUCCANEER?" -> single combat   ; 0x108A
        print "THE BATTLE IS OVER, THE PATRONS RETURN TO DRINKING."  ; 0x10F5

  end   ; opcode 0x00 (STOP)  or  chain_to_ecl (0x20)
```

**Verified in this transcript:** every quoted string (decoded byte-exact via §3), the opcode
*vocabulary* present in the block, the `01 <word>` variable-reference idiom, var `0x6DD2`, and that
the content matches Pool of Radiance's documented Podol Plaza auction (cross-checked against the
recovered strings, which name Garwin, the wand of fear, the 5 000 gp bid, the Slums tavern).
**Inferred (UNCERTAIN):** the exact branch ordering, which compare-flag gates which `print`, and
the precise GOTO/label targets — these ride on the un-emulated operand grammar.

---

## 5. Status: verified vs. remaining

**Solidly verified (ship-ready):**
- Interpreter loop `0x03EB7`, dispatch `0x03C73` (TP dense-CASE cmp-chain), all VM state globals.
- 41 opcodes located by handler with disasm-confirmed structure; control-flow ops (STOP, GOTO,
  RETURN, IF family, COMPARE, GOTO_LABEL, CHAIN_TO_ECL) at high confidence.
- The 6-bit text codec — fully cracked, reproduced bit-identically, 92–98 strings recovered per
  block, corroborated against the published game.
- Header is 5 records; `rec0=0x1388` is a constant sentinel (corrected from the offset hypothesis).

**Remaining (open items):**
1. **Operand wire-grammar** — emulate the resident `0x2B` helper segment (it self-relocates;
   needs a tiny 16-bit emulator seeded from START.EXE far-call resolution) to get byte-exact
   operand widths and thus a fully linearized disassembly + reproducible re-assembler.
2. **Header entry-point resolution** — recs 1–4 `&0x7FFF` are not raw offsets; the same `0x2B`
   helper resolves them. Decoding (1) resolves this for free.
3. Raise the 0.50–0.70 opcode rows to proof once (1) lands (operands become legible).

---

## 6. Generalization — the reusable decode-kit pattern for DOS bytecode VMs

This decode followed a repeatable recipe that applies to most late-80s/early-90s DOS engines whose
"content" lives in an interpreted bytecode (SSI Gold Box, SCUMM, AGI/SCI, Magnetic Scrolls, etc.):

1. **Find the interpreter, not the data, first.** The data is meaningless until you have the loop.
   Score every function prologue (here TP `55 89 E5`) by a *selector signature*: a contiguous set
   of `cmp al,imm8` with `imm8 ≤ opcode_max`, combined with a byte-buffer read. The fetch loop and
   the dispatcher fall out of that.
2. **Identify the PC, the buffer pointer, and the opcode latch** as fixed globals. The loop that
   does `les di,[buf]; add di,pc; mov al,es:[di+bias]; mov [op],al; call dispatch` is the tell.
3. **Don't assume a jump table.** High-level-language compilers (Turbo Pascal, early C) emit dense
   `CASE`/`switch` as cmp-chains or range-helpers. A jump-table scan returning nothing is a *signal*
   that the dispatch is a compiled CASE, not absence of a VM.
4. **Resolve far-calls through the loader's relocation model.** Here START.EXE self-relocates with
   0 relocations, so `seg:off → file_off = 0x200 + seg*16 + off`. Establish this once; it makes
   every helper call legible and lets you separate *language runtime* (ignore) from *game helpers*.
5. **Recover opcodes by their side effects on known globals** (PC writes = jumps; stop-flag sets =
   END; FreeMem/list-walks = teardown; video-segment blits = draw; flag-bank tests = IF). You can
   name 80% of an opcode set from effects alone, before fully decoding operands.
6. **Crack the text codec by following the print opcode inward.** The string decompressor lives in
   the print handler's call tree. A packed-bit (5/6-bit) scheme + a small char remap is the common
   case; verify by brute-forcing alignment and scoring for natural-language output, then confirm
   bit-for-bit against the engine routine.
7. **Cross-check against ground truth** (manuals, the actual playable game). Recovered strings that
   match published content prove the codec *and* anchor the event semantics.
8. **Be honest about the helper boundary.** Operand grammars are frequently produced by a resident
   helper segment that won't statically reduce; the honest finish is a small 16-bit emulator of
   just that helper, seeded from the relocation model in step 4.

"Decode any old game — Pool of Radiance is Exhibit A": steps 1–7 are tool-agnostic (capstone +
Python), and the `kit/dax.py` + `ecl_textcodec.py` + prologue-scoring scripts in `analysis/` are
the portable scaffolding.

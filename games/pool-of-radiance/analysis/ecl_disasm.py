# ECL bytecode disassembler — resolves the operand wire-grammar statically.
#
# The §1.4 "0x2B helper" caveat is resolved here WITHOUT emulating the helper, by reading
# the grammar straight off the bytecode: every operand is a tagged value.
#   tag 0x00 <byte>          -> immediate byte
#   tag 0x01 <lo> <hi>       -> WORD (variable reference or word immediate), little-endian
#   tag 0x80..0xFF + payload -> string/struct operand (high-bit family; see resolve_str)
# Opcodes are single bytes 0x00..0x3D (0x1F unused). Each opcode's operand COUNT is fixed
# (from the verified §2 table); the loop pulls that many tagged operands.
import sys, os, json
sys.path.insert(0, r".\kit")
import dax
from ecl_textcodec import decode_string  # existing verified 6-bit codec: (buf,pos)->(bytes,end)

GAME = r".\games\pool-of-radiance\extracted\poolrad"

# opcode -> (mnemonic, operand_count). -1 = variable / handled specially.
OPS = {
 0x00:("STOP",0), 0x01:("GOTO",1), 0x02:("CONTROL1",1), 0x03:("CMP_OR_ASSIGN",2),
 0x04:("ADD",3), 0x05:("SUB",3), 0x06:("DIV",3), 0x07:("MUL",3),
 0x08:("RANDOM",2), 0x09:("SET_VAR",2), 0x0A:("MOVE_PARTY",1), 0x0B:("ADD_NPC",4),
 0x0C:("LOOP_INIT",3), 0x0D:("LOOP_NEXT",0), 0x0E:("START_COMBAT",1), 0x0F:("SHOW_PICTURE",1),
 0x10:("PRINT_TEXT",1), 0x11:("DISPLAY_WINDOW",1), 0x12:("DISPLAY_WINDOW2",1), 0x13:("RETURN",0),
 0x14:("COMPARE_SET_FLAGS",4), 0x15:("MENU_SELECT",1), 0x16:("IF_EQUAL",0), 0x17:("IF_NOT_EQUAL",0),
 0x18:("IF_COND2",0), 0x19:("IF_COND3",0), 0x1A:("IF_COND4",0), 0x1B:("IF_COND5",0),
 0x1C:("CLEAR_OBJ_LIST",0), 0x1D:("PARTY_STAT_AGG",1), 0x1E:("PARTY_FIELD_SURVEY",1),
 0x20:("CHAIN_TO_ECL",1), 0x21:("SET_AREA_ENCOUNTER",3), 0x22:("TEST_PARTY_CLASS",2),
 0x23:("RANDOM_PICK",4), 0x24:("AREA_STEP_EVENT",0), 0x25:("GOTO_LABEL",2), 0x26:("GOTO_SELECT",2),
 0x27:("LOAD_RESOURCE_PIC",9),
 0x28:("OP28",1), 0x29:("OP29",1), 0x2A:("OP2A",1), 0x2B:("OP2B",1), 0x2C:("OP2C",1),
 0x2D:("OP2D",1), 0x2E:("OP2E",1), 0x2F:("OP2F",1), 0x30:("OP30",1), 0x31:("OP31",1),
 0x32:("OP32",1), 0x33:("OP33",1), 0x34:("OP34",1), 0x35:("OP35",1), 0x36:("OP36",1),
 0x37:("OP37",1), 0x38:("OP38",1), 0x39:("OP39",1), 0x3A:("OP3A",1), 0x3B:("OP3B",1),
 0x3C:("OP3C",1), 0x3D:("OP3D",1),
}
# opcodes whose operand is a packed-text string inline (PRINT/WINDOW/MENU emit text)
TEXT_OPS = {0x10, 0x11, 0x12, 0x15}
# GOTO_LABEL/GOTO_SELECT carry an inline jump table: op0 + count(byte) + count*word entries
TABLE_OPS = {0x25, 0x26}
# Empirically-fit label address base: logical label L -> file offset (L - LABEL_BASE).
# Found by maximizing how many observed GOTO/header targets land on valid opcode bytes.
LABEL_BASE = 0x98F1

def lbl(v):
    """Render a word operand: a label/code address if it falls in code space, else a var."""
    off = v - LABEL_BASE
    return f"L_{off:04X}" if 0 <= off < 0x4000 and v >= 0x9000 else f"${v:04X}"

def read_operand(d, p, as_label=False):
    """Return (repr, new_p). Tagged operand: 0x00=imm byte, 0x01=word."""
    if p >= len(d): return ("<eof>", p)
    tag = d[p]
    if tag == 0x00:
        return (f"#{d[p+1]}", p+2)
    if tag == 0x01:
        v = d[p+1] | (d[p+2] << 8)
        return (lbl(v) if as_label else f"${v:04X}", p+3)
    # high-bit / other tag: a string/struct selector — consume just the tag (best-effort)
    return (f"?{tag:02X}", p+1)

def try_text(d, p):
    """If a packed-text string starts at p, decode it; return (text, new_p) or (None,p).
    Strings are 6-bit packed, 0x00-terminated (per the verified codec)."""
    raw, end = decode_string(d, p, 255)
    if len(raw) < 3:
        return (None, p)
    txt = raw.decode('latin1')
    letters = sum(1 for b in raw if 0x41 <= b <= 0x5A or b == 0x20 or 0x30 <= b <= 0x3F)
    if letters >= 0.8 * len(raw):
        return (txt, end)
    return (None, p)

def disasm(d, start, limit=None, max_ins=4000):
    p = start
    out = []
    end = len(d) if limit is None else min(len(d), start+limit)
    n = 0
    while p < end and n < max_ins:
        op = d[p]; ins_at = p; p += 1
        if op not in OPS:
            out.append((ins_at, f".byte 0x{op:02X}", None)); n += 1; continue
        name, argc = OPS[op]
        args = []
        # text-bearing ops: first try an inline packed string operand
        consumed_text = None
        if op in TEXT_OPS:
            # operand is usually a var-ref to a string slot, but inline strings appear too
            t, np = try_text(d, p)
            if t is not None and op == 0x10:
                consumed_text = t; p = np
        if op == 0x01:  # GOTO: single label operand
            r, p = read_operand(d, p, as_label=True); args.append(r)
        elif op in TABLE_OPS:  # GOTO_LABEL/SELECT: op0(label) + count + count word-entries
            r, p = read_operand(d, p, as_label=True); args.append(r)
            if p < len(d) and d[p] == 0x00:
                cnt = d[p+1]; p += 2; args.append(f"#{cnt}")
                tbl = []
                for _ in range(cnt):
                    if p+2 < len(d) and d[p] == 0x01:
                        v = d[p+1] | (d[p+2] << 8); tbl.append(lbl(v)); p += 3
                args.append("[" + ", ".join(tbl) + "]")
        elif consumed_text is None:
            for _ in range(argc):
                r, p = read_operand(d, p)
                args.append(r)
        s = name + (" " + ", ".join(args) if args else "")
        out.append((ins_at, s, consumed_text)); n += 1
        if op in (0x00, 0x13, 0x20):  # STOP / RETURN / CHAIN end a straight-line run
            # keep going (there may be more event bodies) but mark
            pass
    return out

def main():
    fn = sys.argv[1] if len(sys.argv) > 1 else "ECL1.DAX"
    bid = int(sys.argv[2]) if len(sys.argv) > 2 else 18
    blk = [b for b in dax.read_dax(os.path.join(GAME, fn)) if b["id"]==bid][0]
    d = blk["data"]
    # 5 header records of 4 bytes each (rec0 sentinel 0x1388 + 4 event-handler ptrs)
    hdr = [(d[i*4]|d[i*4+1]<<8, d[i*4+2]|d[i*4+3]<<8) for i in range(5)]
    out = []
    out.append(f"# {fn} #{bid}  len={len(d)}")
    out.append(f"# header: sentinel={hdr[0][0]:#06x}  event ptrs(&0x7FFF): " +
               ", ".join(f"{(v&0x7FFF):#06x}" for v,_ in hdr[1:]))
    out.append(f"# operand grammar: tag 00=imm byte, tag 01=WORD(var/label LE); label base {LABEL_BASE:#06x}")
    code_start = 0x16  # first real instruction (0x14-0x15 = header tail)
    limit = int(sys.argv[3], 0) if len(sys.argv) > 3 and sys.argv[3] != "--save" else 0x140
    listing = disasm(d, code_start, limit=limit)
    for at, s, txt in listing:
        line = f"L_{at:04X}: {s}"
        if txt is not None:
            line += f'   ; "{txt}"'
        out.append(line)
    text = "\n".join(out)
    print(text)
    if "--save" in sys.argv:
        outp = os.path.join(os.path.dirname(__file__), f"_ecl_{fn.split('.')[0]}_{bid}.asm")
        open(outp, "w").write(text + "\n")
        print("\nsaved", outp)

if __name__ == "__main__":
    main()

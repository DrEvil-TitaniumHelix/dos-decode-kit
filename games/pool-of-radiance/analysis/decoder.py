import sys
sys.path.insert(0, 'kit')
import dax, struct
from collections import Counter

base = 'games/pool-of-radiance/extracted/poolrad/'
allblocks = []
for n in range(1, 9):
    for b in dax.read_dax(base + f'ECL{n}.DAX'):
        allblocks.append((n, b['id'], b['data']))

# OPERAND MODEL (Gold Box ECL is known to use a tagged-operand scheme).
# An "argument" is read by a routine GetArg: first byte = TAG selecting how to read.
# From the byte patterns we see these arg encodings:
#   tag 0x01: followed by 2 bytes  -> memory/variable WORD  (01 D2 6D)
#   tag 0x03: followed by 2 bytes  -> ? (03 01 .. but 03 then 01-tag?). Re-examine.
# Actually re-look: "03 01 34 4A" — could be opcode 0x03 with arg "01 34 4A"? i.e.
#   0x03 is an OPCODE, and 0x01 W is its single tagged operand.
# And "09 00 02 01 D2 6D" = opcode 0x09, operands "00 02"?? + "01 D2 6D"?
#
# Let's define: each instruction = OPCODE, then a fixed number of TAGGED ARGS per opcode,
# where a TAGGED ARG = tagbyte + payload:
#   tag 0x00 -> +1 byte  (00 02 -> const byte 0x02)
#   tag 0x01 -> +2 bytes (01 D2 6D -> word/var)
#   ... unknown.
# This is hard without the engine. Instead, EMPIRICAL TILING:
# Define arg-reader: read one operand starting at p.
#   first byte t:
#     t==0x00 : operand = next 1 byte         (len 2)
#     t==0x01 : operand = next 2 bytes (WORD)  (len 3)
#     else    : operand = the byte itself (immediate small int) (len 1)
# Then instruction = opcode + N args where N is unknown. Try: greedily, an instruction is
# opcode followed by zero-or-more args until we hit the next opcode... circular.
#
# Better empirical test: TREAT EVERY BYTE position; build a "follow-set" model.
# Strongest signal: the pair "01 <W>" where W in 0x6Dxx..0x6Exx (variable bank) OR 0x4Axx, 0x49xx,
# 0xC0xx, 0x99xx (code/string addrs). Let's confirm 01 is an operand-tag by checking the high
# byte distribution of the WORD after 0x01.
hi = Counter()
for n,bid,d in allblocks:
    bc=d[20:]
    i=0;L=len(bc)
    while i+3<=L:
        if bc[i]==0x01:
            w=bc[i+1]|(bc[i+2]<<8)
            hi[w>>8]+=1
            i+=3
        else:
            i+=1
print("high byte of WORD following 0x01 (var banks):")
for v,ct in hi.most_common(20):
    print(f"  0x{v:02X}xx: {ct}")

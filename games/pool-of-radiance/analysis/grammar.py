import sys
sys.path.insert(0, 'kit')
import dax, struct
from collections import Counter

base = 'games/pool-of-radiance/extracted/poolrad/'
allblocks = []
for n in range(1, 9):
    for b in dax.read_dax(base + f'ECL{n}.DAX'):
        allblocks.append((n, b['id'], b['data']))

allbc = [d[20:] for _, _, d in allblocks]

# HYPOTHESIS: instructions are <opcode byte> <operands>. Operands are themselves typed:
#   0x01 W   : variable/address operand (2 bytes follow)   "01 D2 6D"
#   0x03 W   : another operand type
#   0x09 W   : immediate operand
# The first byte after a complete instruction is the next opcode.
# To find opcodes, find bytes that are followed by a recognizable operand-token run.
#
# Approach: model an instruction as: OPCODE, then a sequence of ARG tokens, each ARG token is
#   tag byte in {0x01,0x03,0x05,0x09,0x0C,...} + 2 byte payload, OR maybe variable.
# Test: take the operand tags we *think* exist and see if "OPCODE (TAG W)*" tiles the stream.
#
# First: histogram of byte that immediately FOLLOWS a "01 <W>" token (i.e., end of an 01-arg).
nxt = Counter()
for bc in allbc:
    i = 0
    L = len(bc)
    while i + 3 <= L:
        if bc[i] == 0x01:
            if i+3 < L:
                nxt[bc[i+3]] += 1
            i += 3
        else:
            i += 1
print("byte following a '01 W' token (candidate next-opcode or next-arg-tag):")
for v, ct in nxt.most_common(25):
    print(f"  0x{v:02X}: {ct}")

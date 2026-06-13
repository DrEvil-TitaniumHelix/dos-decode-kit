import sys
sys.path.insert(0, 'kit')
import dax, struct
from collections import Counter

base = 'games/pool-of-radiance/extracted/poolrad/'
allblocks = []
for n in range(1, 9):
    for b in dax.read_dax(base + f'ECL{n}.DAX'):
        allblocks.append((n, b['id'], b['data']))

# Dump bytes around each in-range handler offset. The byte AT the offset should be an opcode.
lead = Counter()
for n, bid, d in allblocks:
    bc = d[20:]
    L = len(bc)
    for i in range(1, 5):  # skip rec0 (always 0)
        v = struct.unpack_from('<H', d, i*4)[0]
        bo = (v & 0x7FFF) - 5000
        if 0 <= bo < L:
            lead[bc[bo]] += 1
            if n <= 3 and bid in (18, 9):
                ctx = ' '.join(f'{x:02X}' for x in bc[bo:bo+16])
                print(f"ECL{n} id{bid} handler{i}@{bo}: {ctx}")
print()
print("leading byte at handler offsets (should be opcodes):")
for v, ct in lead.most_common():
    print(f"  0x{v:02X}: {ct}")

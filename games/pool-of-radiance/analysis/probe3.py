import sys
sys.path.insert(0, 'kit')
import dax, struct
from collections import Counter

base = 'games/pool-of-radiance/extracted/poolrad/'
allblocks = []
for n in range(1, 9):
    for b in dax.read_dax(base + f'ECL{n}.DAX'):
        allblocks.append((n, b['id'], b['data']))

# Targets: collect handler boundary byte-offsets (in bytecode coords, 0 = byte20)
# byteoff = (v&0x7FFF) - 5000  ; valid if 0 <= byteoff < len-20
def targets(d):
    L = len(d) - 20
    out = []
    for i in range(5):
        v = struct.unpack_from('<H', d, i*4)[0]
        bo = (v & 0x7FFF) - 5000
        out.append(bo)
    return out, L

# Look at the start of the bytecode of several blocks to eyeball the instruction stream.
for n, bid, d in allblocks[:3]:
    bc = d[20:]
    print(f"=== ECL{n} id{bid} bytecode len={len(bc)} ===")
    print(' '.join(f'{x:02X}' for x in bc[:80]))
    t, L = targets(d)
    print("targets(byteoff):", t, "L=", L)
    print()

# Frequency of leading bytes if we treat byte0 of each "instruction" ... but we don't know lengths.
# Instead: study the global byte histogram and bigram structure.
allbc = b''.join(d[20:] for _, _, d in allblocks)
print("total bytecode bytes:", len(allbc))
c = Counter(allbc)
print("top 20 byte values:")
for v, ct in c.most_common(20):
    print(f"  0x{v:02X}: {ct}")

import sys
sys.path.insert(0, 'kit')
import dax, struct
from collections import Counter

base = 'games/pool-of-radiance/extracted/poolrad/'
allblocks = []
for n in range(1, 9):
    for b in dax.read_dax(base + f'ECL{n}.DAX'):
        allblocks.append((n, b['id'], b['data']))

n, bid, d = allblocks[0]
print(f"ECL{n} id{bid} len={len(d)}")
print("first 64 bytes hex:")
print(' '.join(f'{x:02X}' for x in d[:64]))
print("\nbytes 20..120:")
print(' '.join(f'{x:02X}' for x in d[20:120]))
print("\nlast 32 bytes:")
print(' '.join(f'{x:02X}' for x in d[-32:]))

# 0x1388 = 5000. Block len 6550. Maybe header is bigger.
# Look at the structure: maybe records continue past 5. Find where the WORD,01,01 pattern stops.
print("\nscan [.. 01 01] pattern as 4-byte records from offset 0:")
off = 0
recs = []
while off + 4 <= len(d):
    v = struct.unpack_from('<H', d, off)[0]
    b2, b3 = d[off+2], d[off+3]
    if b2 == 1 and b3 == 1:
        recs.append((off, v))
        off += 4
    else:
        break
print(f"  contiguous [x x 01 01] records: {len(recs)} -> stops at byte {off}")
for o, v in recs[:12]:
    print(f"   @{o}: 0x{v:04X} ({v & 0x7FFF})")

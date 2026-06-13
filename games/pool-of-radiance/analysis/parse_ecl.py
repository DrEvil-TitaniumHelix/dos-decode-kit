import sys
sys.path.insert(0, 'kit')
import dax, struct
from collections import Counter

base = 'games/pool-of-radiance/extracted/poolrad/'

def parse_header(d):
    recs = []
    for i in range(5):
        off = i * 4
        val = struct.unpack_from('<H', d, off)[0]
        recs.append((val, d[off+2], d[off+3]))
    return recs

allblocks = []
for n in range(1, 9):
    blocks = dax.read_dax(base + f'ECL{n}.DAX')
    for b in blocks:
        allblocks.append((n, b['id'], b['data']))

print("total blocks:", len(allblocks))
for n, bid, d in allblocks[:8]:
    if len(d) < 20:
        print(f"ECL{n} id{bid} len={len(d)} TOO SHORT"); continue
    recs = parse_header(d)
    print(f"ECL{n} id{bid} len={len(d)}")
    for i, (v, b2, b3) in enumerate(recs):
        off = v & 0x7FFF
        print(f"   rec{i}: val=0x{v:04X} off={off} b2={b2} b3={b3} hibit={'Y' if v&0x8000 else 'n'}")

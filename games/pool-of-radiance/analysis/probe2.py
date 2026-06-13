import sys
sys.path.insert(0, 'kit')
import dax, struct

base = 'games/pool-of-radiance/extracted/poolrad/'
allblocks = []
for n in range(1, 9):
    for b in dax.read_dax(base + f'ECL{n}.DAX'):
        allblocks.append((n, b['id'], b['data']))

# Hypothesis: header values are absolute load addresses; base = rec0 = 0x1388 = 5000.
# local byte offset into block = (value & 0x7FFF) - 5000 + 20 ??? test alignment / range.
for n, bid, d in allblocks:
    vals = [struct.unpack_from('<H', d, i*4)[0] for i in range(5)]
    base_addr = vals[0]  # 0x1388 always
    L = len(d)
    print(f"ECL{n} id{bid} len={L} base=0x{base_addr:04X}")
    for i, v in enumerate(vals):
        a = v & 0x7FFF
        # if base maps to start of bytecode (byte 20) or byte 0?
        off_from_bc = a - base_addr        # if base addr == bytecode start
        loc20 = 20 + off_from_bc
        ok = 0 <= loc20 < L
        print(f"   rec{i} val=0x{v:04X} a={a} -> off_from_base={off_from_bc} loc(@20)={loc20} {'OK' if ok else 'OOR'}")
    if bid != allblocks[0][1]:
        pass
    print()

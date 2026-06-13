import os, sys
sys.path.insert(0, r".\kit")
import dax
GAME=r".\games\pool-of-radiance\extracted\poolrad"
# WALLDEF files
for fn in sorted(f for f in os.listdir(GAME) if f.startswith("WALLDEF")):
    b=dax.read_dax(os.path.join(GAME,fn))
    print(f"{fn}: ids={[e['id'] for e in b]}")
    e=b[0]; d=e["data"]
    print(f"  block0 id={e['id']} len={len(d)}: {' '.join(f'{x:02X}' for x in d[:32])}")
# Re-examine 8X8D1 structure: full hexdump of decompressed block id1
print("\n=== 8X8D1 block id=1 (first 96 bytes decompressed) ===")
d=dax.read_dax(os.path.join(GAME,"8X8D1.DAX"))[0]["data"]
for off in range(0,96,16):
    print(f"  {off:03d}: "+" ".join(f"{x:02X}" for x in d[off:off+16]))
print(f"  total len={len(d)}; len-4={len(d)-4}; /32={(len(d)-4)/32:.2f}; /64={(len(d)-4)/64:.2f}")
# all 8X8D block sizes
print("\n8X8D block sizes:")
for i in range(1,9):
    p=os.path.join(GAME,f"8X8D{i}.DAX")
    if os.path.exists(p):
        for e in dax.read_dax(p): print(f"  8X8D{i} id={e['id']:3d} len={len(e['data'])}")

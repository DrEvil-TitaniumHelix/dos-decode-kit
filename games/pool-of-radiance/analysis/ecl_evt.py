import os, sys, struct
sys.path.insert(0, r".\kit")
import dax
GAME=r".\games\pool-of-radiance\extracted\poolrad"
for fn,idx in [("ECL1.DAX",0),("ECL3.DAX",0)]:
    e=dax.read_dax(os.path.join(GAME,fn))[idx]; d=e["data"]
    recs=[struct.unpack_from("<H",d,k*4)[0] for k in range(5)]
    print(f"\n=== {fn} id={e['id']} len={len(d)} (0x{len(d):04X}) ===")
    print(f"  records: {[f'0x{v:04X}' for v in recs]}")
    for k,v in enumerate(recs):
        off=v & 0x7FFF
        tag='within' if off<len(d) else 'PAST-END'
        peek=' '.join(f'{d[off+j]:02X}' for j in range(8)) if off+8<=len(d) else '(oob)'
        print(f"   rec{k}: 0x{v:04X} hi={v>>15} off=0x{off:04X} [{tag}] -> {peek}")
    # also try off = v - 0x1388 (relative to the constant)?
    print("  alt (v - 0x8000):")
    for k,v in enumerate(recs[1:],1):
        off=v-0x8000
        if 0<=off<len(d):
            print(f"   rec{k}: off=0x{off:04X} -> {' '.join(f'{d[off+j]:02X}' for j in range(8))}")

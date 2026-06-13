import os, sys
sys.path.insert(0, r".\kit")
import dax
GAME=r".\games\pool-of-radiance\extracted\poolrad"
# all DAX files + sizes (look for title/pic art)
print("=== all DAX files ===")
for f in sorted(os.listdir(GAME)):
    if f.endswith(".DAX"):
        p=os.path.join(GAME,f); 
        try:
            b=dax.read_dax(p); print(f"  {f:14s} {len(b):3d} blocks, ids={[e['id'] for e in b][:6]}")
        except Exception as ex: print(f"  {f:14s} ERR {ex}")
# CHRDATA.ITM structure
print("\n=== CHRDATA1.ITM ===")
b=open(os.path.join(GAME,"CHRDATA1.ITM"),"rb").read()
print(f"  {len(b)} bytes")
import re
for off in range(0,len(b),16):
    print(f"  {off:03d}: "+" ".join(f"{x:02X}" for x in b[off:off+16])+"  "+''.join(chr(x) if 32<=x<127 else '.' for x in b[off:off+16]))

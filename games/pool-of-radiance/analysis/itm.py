import os, re
GAME=r".\games\pool-of-radiance\extracted\poolrad"
for n in [1,3,6]:
    b=open(os.path.join(GAME,f"CHRDATA{n}.ITM"),"rb").read()
    print(f"\n=== CHRDATA{n}.ITM ({len(b)} bytes) ===")
    # find readable item names
    strs=re.findall(rb"[\x20-\x7e]{3,}", b)
    print("  strings:", [s.decode() for s in strs])
    for off in range(0,min(len(b),96),16):
        print(f"  {off:03d}: "+" ".join(f"{x:02X}" for x in b[off:off+16])+"  "+''.join(chr(x) if 32<=x<127 else '.' for x in b[off:off+16]))
# ITEMS master file
it=open(os.path.join(GAME,"ITEMS"),"rb").read()
print(f"\n=== ITEMS ({len(it)} bytes) ===")
strs=re.findall(rb"[\x20-\x7e]{4,}", it)
print("  item names:", [s.decode() for s in strs[:40]])

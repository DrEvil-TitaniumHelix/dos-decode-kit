import os, sys, re
sys.path.insert(0, r".\kit")
import dax
GAME=r".\games\pool-of-radiance\extracted\poolrad"
for fn in ["ECL1.DAX","ECL3.DAX"]:
    b=dax.read_dax(os.path.join(GAME,fn))
    print(f"\n=== {fn}: ids={[e['id'] for e in b]} ===")
    for e in b[:2]:
        d=e["data"]
        strs=re.findall(rb"[\x20-\x7e]{6,}", d)
        print(f"  block id={e['id']} len={len(d)}; {len(strs)} strings; first bytes: {' '.join(f'{x:02X}' for x in d[:16])}")
        for s in strs[:6]:
            print(f"     {s.decode()!r}")

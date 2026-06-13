import os, sys, re
sys.path.insert(0, r".\kit")
import dax
GAME=r".\games\pool-of-radiance\extracted\poolrad"
for fn in ["ITEM1.DAX","ITEM2.DAX","ITEM4.DAX"]:
    p=os.path.join(GAME,fn)
    if not os.path.exists(p): print(fn,"missing"); continue
    blocks=dax.read_dax(p)
    print(f"\n=== {fn}: {len(blocks)} blocks ===")
    for e in blocks[:2]:
        d=e["data"]
        strs=[s.decode() for s in re.findall(rb"[\x20-\x7e]{3,}", d)]
        print(f"  block id={e['id']} len={len(d)}; {len(strs)} strings:")
        for s in strs[:25]: print(f"      {s!r}")

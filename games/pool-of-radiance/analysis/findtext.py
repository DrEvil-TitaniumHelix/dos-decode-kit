import os, sys, re
sys.path.insert(0, r".\kit")
import dax
GAME=r".\games\pool-of-radiance\extracted\poolrad"
# english-ish: runs with common words
WORDS=re.compile(rb"(?i)\b(the|you|your|and|with|have|are|this|that|will|here|room|door|gold|attack|party)\b")
def score(buf):
    s=re.findall(rb"[\x20-\x7e]{10,}", buf)
    return sum(len(WORDS.findall(x)) for x in s), s
print("=== scanning all files (raw) for English text ===")
for f in sorted(os.listdir(GAME)):
    p=os.path.join(GAME,f)
    if not os.path.isfile(p): continue
    b=open(p,"rb").read()
    sc,strs=score(b)
    if sc>=3:
        good=[x.decode() for x in strs if len(WORDS.findall(x))>=1][:3]
        print(f"  {f:16s} score={sc:3d}  e.g. {good}")
# also try decompressing DAX blocks and scanning
print("\n=== scanning DECOMPRESSED dax blocks ===")
for f in sorted(os.listdir(GAME)):
    if not f.endswith(".DAX"): continue
    try: blocks=dax.read_dax(os.path.join(GAME,f))
    except: continue
    for e in blocks:
        sc,strs=score(e["data"])
        if sc>=4:
            good=[x.decode() for x in strs if len(WORDS.findall(x))>=2][:2]
            if good: print(f"  {f} id={e['id']} score={sc}  {good}")

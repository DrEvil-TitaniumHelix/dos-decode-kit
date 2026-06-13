import os, sys, re
sys.path.insert(0, r".\kit")
import dax
GAME=r".\games\pool-of-radiance\extracted\poolrad"
# concatenate all ECL data
data=b""
for i in range(1,9):
    p=os.path.join(GAME,f"ECL{i}.DAX")
    if os.path.exists(p):
        for e in dax.read_dax(p): data+=e["data"]
COMMON=set(b"etaoinshrdlu ")
def score(buf):
    # count common-English bytes + ' the '/' and '/'you'
    s=sum(1 for b in buf if b in COMMON)
    t=buf.count(b' the ')+buf.count(b'you')+buf.count(b'The ')+buf.count(b' and ')
    return s + t*500
best=(score(data),'raw',data[:0])
# try ADD/SUB const, XOR const
for op in ['add','sub','xor']:
    for k in range(1,128):
        if op=='add': dec=bytes((b+k)&0xFF for b in data)
        elif op=='sub': dec=bytes((b-k)&0xFF for b in data)
        else: dec=bytes(b^k for b in data)
        sc=score(dec)
        if sc>best[0]: best=(sc,f"{op} {k}",dec)
print(f"best transform: {best[1]} (score {best[0]} vs raw {score(data)})")
ms=re.findall(rb"[a-z][a-z ]{6,}", best[2])
print("sample lowercase runs:", [m.decode() for m in ms[:12]])
# Also: maybe text is only in a region. Find longest run of bytes that are mostly letters after best transform

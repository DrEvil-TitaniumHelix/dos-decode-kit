from capstone import Cs, CS_ARCH_X86, CS_MODE_16
import struct
from collections import Counter
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ov=open(GAME+r"\GAME.OVR","rb").read()
md=Cs(CS_ARCH_X86, CS_MODE_16)

# TRUE Pascal prologue: 55 89 E5 (push bp; mov bp,sp). Also accept 55 8B EC.
def find_all(pat):
    out=[]; i=ov.find(pat)
    while i!=-1: out.append(i); i=ov.find(pat,i+1)
    return out
p1=find_all(b"\x55\x89\xe5"); p2=find_all(b"\x55\x8b\xec")
funcs=sorted(set(p1+p2))
print(f"Pascal function prologues: 55 89 E5={len(p1)}, 55 8B EC={len(p2)}, total unique={len(funcs)}")

# near-call graph -> caller count per function
calls=Counter()
i=0
while i<len(ov)-3:
    if ov[i]==0xE8:
        rel=struct.unpack_from("<h",ov,i+1)[0]; t=i+3+rel
        if 0<=t<len(ov): calls[t]+=1
    i+=1
# map call targets that land on/near a known prologue
fset=set(funcs)
hot=[(f,calls.get(f,0)) for f in funcs]
hot.sort(key=lambda x:-x[1])
print(f"\nTop 12 functions by direct near-call count (of {len(funcs)} funcs):")
for f,c in hot[:12]:
    # frame size if sub sp follows
    fl=""
    win=ov[f:f+8]
    if win[3]==0x83 and win[4]==0xEC: fl=f"locals={win[5]}"
    elif win[3]==0x81 and win[4]==0xEC: fl=f"locals={struct.unpack_from('<H',win,5)[0]}"
    print(f"  0x{f:05X}: {c:3d} callers  {fl}")

# segment-call histogram: which runtime segments host the hot helpers (9A off16 seg16)
segc=Counter()
i=0
while i<len(ov)-5:
    if ov[i]==0x9A:
        off,seg=struct.unpack_from("<HH",ov,i+1)
        # filter to plausible: seg small-ish, appears repeatedly
        segc[seg]+=1
    i+=1
print("\nMost-targeted far-call SEGMENTS (library/runtime hosts):")
for seg,c in segc.most_common(10):
    print(f"  seg 0x{seg:04X}: {c} far-calls")

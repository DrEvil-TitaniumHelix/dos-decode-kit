import math
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ov=open(GAME+r"\GAME.OVR","rb").read()
def H(buf):
    if not buf: return 0
    c=[0]*256
    for x in buf: c[x]+=1
    h=0
    for n in c:
        if n: p=n/len(buf); h-=p*math.log2(p)
    return h
W=0x1000
print(f"GAME.OVR entropy by 0x1000 window (bits/byte; >7.3 ~ compressed):")
hi=lo=0
for off in range(0,len(ov),W):
    seg=ov[off:off+W]; h=H(seg)
    bar="#"*int(h*4)
    flag="  <-- packed?" if h>7.3 else ("  <-- text/code" if h<5.5 else "")
    if h>7.3: hi+=1
    if h<5.5: lo+=1
    if off < 0x6000 or off > len(ov)-0x4000 or off % 0x8000 < 0x1000:
        print(f"  0x{off:05X}: {h:4.2f} {bar}{flag}")
print(f"\nwindows >7.3 (packed-like): {hi}/{(len(ov)+W-1)//W}   <5.5 (text/code-like): {lo}")
print(f"overall entropy: {H(ov):.3f} bits/byte")
# Look right after the string table: find end of dense-ASCII run
import re
# last big ascii cluster end
asc=re.finditer(rb"[\x20-\x7e]{4,}", ov)
spans=[(m.start(),m.end()) for m in asc]
textbytes=sum(b-a for a,b in spans)
print(f"ascii-string coverage: {textbytes} bytes ({100*textbytes/len(ov):.0f}% of file)")
print(f"last string near: 0x{spans[-1][0]:05X}; first string: 0x{spans[0][0]:05X}")

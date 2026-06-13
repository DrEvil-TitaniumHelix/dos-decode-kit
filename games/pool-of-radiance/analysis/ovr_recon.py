import struct
from collections import Counter
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ov=open(GAME+r"\GAME.OVR","rb").read()

# 1) Structural anchors
print("=== STRUCTURAL ANCHORS (raw byte signatures) ===")
print(f" int Nh  (CD xx):   total {ov.count(0xCD)}")
print(f"   int 10h (CD 10) video BIOS: {ov.count(bytes([0xCD,0x10]))}")
print(f"   int 21h (CD 21) DOS:        {ov.count(bytes([0xCD,0x21]))}")
print(f"   int 16h (CD 16) keyboard:   {ov.count(bytes([0xCD,0x16]))}")
print(f"   int 33h (CD 33) mouse:      {ov.count(bytes([0xCD,0x33]))}")
print(f" far call 9A: {ov.count(0x9A)}   near call E8: {ov.count(0xE8)}   far ret CB: {ov.count(0xCB)}   near ret C3: {ov.count(0xC3)}")
# video segment immediates: mov ax,imm = B8 lo hi
def find_imm_movax(seg):
    pat=bytes([0xB8, seg&0xFF, (seg>>8)&0xFF]); n=0; i=ov.find(pat)
    locs=[]
    while i!=-1: locs.append(i); n+=1; i=ov.find(pat,i+1)
    return locs
for seg,name in [(0xA000,"EGA graphics A000"),(0xB800,"text B800"),(0x0040,"BIOS data 0040")]:
    locs=find_imm_movax(seg)
    print(f" mov ax,{seg:04X}h ({name}): {len(locs)} sites" + (f"  first @0x{locs[0]:05X}" if locs else ""))

# 2) Near-call (E8) target histogram WITHIN a code region (self-relative, no fixup needed)
print("\n=== NEAR-CALL GRAPH (E8 rel16, fixup-free) — hottest callees ===")
# scan plausible code area (skip the very front data); collect call targets
calls=Counter()
i=0x300
while i < len(ov)-3:
    if ov[i]==0xE8:
        rel=struct.unpack_from("<h",ov,i+1)[0]
        tgt=(i+3+rel)
        if 0 <= tgt < len(ov):
            calls[tgt]+=1
    i+=1
hot=calls.most_common(15)
for tgt,c in hot:
    print(f"  callee @0x{tgt:05X}: called {c}x")

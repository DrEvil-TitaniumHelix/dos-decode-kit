import os, sys
sys.path.insert(0, r".\kit")
import dax
from PIL import Image
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\extracted_assets"
# Search GAME.OVR + START.EXE for an 8x8 1bpp font. Heuristic: the SPACE glyph (char 0x20)
# is 8 zero bytes; uppercase A-Z follow a structured pattern. Score windows where
# offset+0x20*8 .. +0x20*8+8 is all-zero AND surrounding bytes have glyph-like bit density.
def find_font(buf, name):
    best=[]
    for base in range(0, len(buf)-2048, 1):
        # candidate: char N glyph at base + N*8. space at base+0x100
        sp=buf[base+0x100:base+0x108]
        if any(sp): continue
        # check 'A'(0x41) and 'E'(0x45) glyphs have ink (nonzero) and aren't full
        def ink(c):
            g=buf[base+c*8:base+c*8+8]; bits=sum(bin(b).count('1') for b in g); return bits
        a=ink(0x41); e=ink(0x45); i=ink(0x49); m=ink(0x4D)
        if 8<a<48 and 8<e<48 and 6<i<40 and 10<m<56:
            # also chars 0x21..0x2F (punct) should mostly have some ink
            score=sum(1 for c in range(0x41,0x5b) if 4<ink(c)<56)
            best.append((score,base))
    best.sort(reverse=True)
    return best[:5]
for fn,buf in [("START.EXE",open(GAME+r"\START.EXE","rb").read()),
               ("GAME.OVR",open(GAME+r"\GAME.OVR","rb").read())]:
    cands=find_font(buf,fn)
    print(f"{fn}: top font candidates (score,offset): {[(s,hex(o)) for s,o in cands]}")
    # render the best candidate
    if cands and cands[0][0]>=20:
        base=cands[0][1]
        im=Image.new("RGB",(16*9,8*9),(20,20,30))
        for c in range(0,128):
            g=buf[base+c*8:base+c*8+8]
            cx=(c%16)*9; cy=(c//16)*9
            for r in range(8):
                for col in range(8):
                    if g[r]&(0x80>>col): im.putpixel((cx+col,cy+r),(230,230,210))
        im.resize((16*9*3,8*9*3),Image.NEAREST).save(os.path.join(OUT,f"_font_{fn}.png"))
        print(f"  rendered _font_{fn}.png at base {hex(base)}")

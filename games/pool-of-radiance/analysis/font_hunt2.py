import os
from PIL import Image
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\extracted_assets"
# Better font scan: a 8x8 font has SPACE(0x20)=blank, and uppercase A-Z structured.
# Strong signal: chars 0x41..0x5A each have ink in 4..7 of the 8 rows (letters fill most rows)
# and the TOP row of most letters has some ink (caps). Score windows; render top 6.
def score(buf, base):
    if base+0x60*8>len(buf): return -1
    if any(buf[base+0x20*8:base+0x20*8+8]): return -1   # space must be blank
    s=0
    for c in range(0x41,0x5b):
        g=buf[base+c*8:base+c*8+8]
        rows_with_ink=sum(1 for b in g if b)
        if 4<=rows_with_ink<=8: s+=1
        # letters rarely have a fully-set byte (0xFF) except maybe bars
        if all(b!=0xFF for b in g): s+=0.2
    return s
def render(buf, base, name):
    im=Image.new("RGB",(16*9,6*9),(15,15,25))
    for c in range(0x20,0x80):
        g=buf[base+c*8:base+c*8+8]; cx=((c-0x20)%16)*9; cy=((c-0x20)//16)*9
        for r in range(8):
            for col in range(8):
                if g[r]&(0x80>>col): im.putpixel((cx+col,cy+r),(240,240,210))
    im.resize((16*9*4,6*9*4),Image.NEAREST).save(os.path.join(OUT,name))
for fn in ["START.EXE","GAME.OVR"]:
    buf=open(os.path.join(GAME,fn),"rb").read()
    cands=sorted(((score(buf,b),b) for b in range(0x200,len(buf)-0x600,8)),reverse=True)[:3]
    print(fn, "top:", [(round(s,1),hex(b)) for s,b in cands])
    if cands and cands[0][0]>20:
        render(buf, cands[0][1], f"_font2_{fn}.png"); print("  rendered _font2_"+fn+".png @",hex(cands[0][1]))

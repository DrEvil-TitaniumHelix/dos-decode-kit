import os, sys
sys.path.insert(0, r".\kit")
import dax
from PIL import Image
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\extracted_assets"
EGA=dax.EGA16
def planar_byplane(buf, wbytes, h, hskip):
    body=buf[hskip:]
    plane=wbytes*h
    W=wbytes*8
    im=Image.new("RGB",(W,h),(0,0,0))
    for y in range(h):
        for bx in range(wbytes):
            b=[body[p*plane + y*wbytes + bx] if p*plane+y*wbytes+bx<len(body) else 0 for p in range(4)]
            for bit in range(8):
                v=0
                for p in range(4):
                    if b[p]&(0x80>>bit): v|=(1<<p)
                im.putpixel((bx*8+bit, y), EGA[v])
    return im
d=dax.read_dax(os.path.join(GAME,"TITLE.DAX"))[0]["data"]
# header: word0=200(h), word1=40(wbytes) -> 320x200. try header skip 4 and 6
for hs in [4,6]:
    im=planar_byplane(d, 40, 200, hs)
    im.resize((640,400),Image.NEAREST).save(os.path.join(OUT,f"_title_planar_h{hs}.png"))
    print("title planar h",hs)

import os, sys
sys.path.insert(0, r".\kit")
import dax
from PIL import Image
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\extracted_assets"
EGA=dax.EGA16
# The rope frame is a fixed screen element. Candidates: BACPAC, or a full-screen image.
# Render BACPAC at several widths; render at 320 to see if it's the border strip.
def render(d,w,hskip=4,scale=2):
    body=d[hskip:]; px=[]
    for b in body: px.append(b>>4); px.append(b&0xF)
    h=(len(px)+w-1)//w
    im=Image.new("RGB",(w,h),(0,0,0))
    for i,p in enumerate(px):
        if i//w<h: im.putpixel((i%w,i//w),EGA[p])
    return im.resize((w*scale,h*scale),Image.NEAREST)
b=dax.read_dax(os.path.join(GAME,"BACPAC.DAX"))[0]["data"]
print("BACPAC len",len(b),"hdr",[hex(x) for x in b[:8]])
# BACPAC hdr 18 00 03 00 -> 0x18=24? try width = 24*?? and full 320. Render a few.
for w,hs in [(320,4),(320,8),(176,8),(48,8),(40,8)]:
    render(b,w,hs,2).save(os.path.join(OUT,f"_bp_{w}_{hs}.png"))
print("rendered BACPAC variants")
# also: maybe the rope is drawn from a small tile in 8X8D or a dedicated file. list any with 'rope/back/frame/bord' in disasm strings? just list sizes of small DAX

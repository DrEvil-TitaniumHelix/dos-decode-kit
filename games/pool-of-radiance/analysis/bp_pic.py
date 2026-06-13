import os, sys
sys.path.insert(0, r".\kit")
import dax
from PIL import Image, ImageDraw
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\extracted_assets"
EGA=dax.EGA16
def render(body,w,scale=1,hskip=4):
    body=body[hskip:]; px=[]
    for byte in body: px.append(byte>>4); px.append(byte&0xF)
    h=(len(px)+w-1)//w
    im=Image.new("RGB",(w,h),(0,0,0))
    for i,p in enumerate(px):
        if i//w<h: im.putpixel((i%w,i//w),EGA[p])
    return im.resize((int(w*scale),int(h*scale)),Image.NEAREST)
# BACPAC at 320 (full width like TITLE) scale 1
b=dax.read_dax(os.path.join(GAME,"BACPAC.DAX"))[0]["data"]
render(b,320,1).save(os.path.join(OUT,"_bacpac320.png")); print("bacpac320:", (len(b)-4)//160,"rows at 320")
# PIC1 block0 width sweep (scene pictures) compact
d=dax.read_dax(os.path.join(GAME,"PIC1.DAX"))[0]["data"]
print("PIC1 b0 len",len(d),"hdr",[hex(x) for x in d[:6]])
widths=[88,96,104,112,120,136]
ims=[render(d,w,2) for w in widths]
Wd=sum(i.width for i in ims)+8*len(ims); Hd=max(i.height for i in ims)
sh=Image.new("RGB",(Wd,Hd+16),(50,50,60)); dr=ImageDraw.Draw(sh); x=4
for w,im in zip(widths,ims): sh.paste(im,(x,14)); dr.text((x,2),str(w),fill=(255,255,0)); x+=im.width+8
sh=sh.crop((0,0,min(sh.width,1980),min(sh.height,1980)))
sh.save(os.path.join(OUT,"_pic_sweep.png")); print("pic swept", sh.size)

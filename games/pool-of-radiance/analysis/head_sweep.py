import os, sys
sys.path.insert(0, r".\kit")
import dax
from PIL import Image, ImageDraw
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\extracted_assets"
EGA=dax.EGA16
d=dax.read_dax(os.path.join(GAME,"HEAD1.DAX"))[0]["data"]
print("HEAD1 block0 len",len(d),"hdr",[hex(x) for x in d[:8]])
def strip(body,w,scale=4):
    px=[]
    for byte in body: px.append(byte>>4); px.append(byte&0xF)
    h=(len(px)+w-1)//w
    im=Image.new("RGB",(w,h),(20,20,30))
    for i,p in enumerate(px):
        if i//w<h: im.putpixel((i%w,i//w),EGA[p])
    return im.resize((w*scale,h*scale),Image.NEAREST)
# try both 4-byte and 8-byte header skip, widths around a head size
widths=[24,32,40,44,48]
for hs in [4,8]:
    body=d[hs:]
    ims=[strip(body,w) for w in widths]
    H=max(i.height for i in ims); W=sum(i.width for i in ims)+8*len(ims)
    sheet=Image.new("RGB",(W,H+16),(50,50,60)); dr=ImageDraw.Draw(sheet); x=4
    for w,im in zip(widths,ims): sheet.paste(im,(x,14)); dr.text((x,2),f"w{w}",fill=(255,255,0)); x+=im.width+8
    sheet.save(os.path.join(OUT,f"_head_sweep_h{hs}.png"))
    print(f"saved _head_sweep_h{hs}.png")

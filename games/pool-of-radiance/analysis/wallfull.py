import os, sys
sys.path.insert(0, r".\kit")
import dax
from PIL import Image, ImageDraw
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\extracted_assets"
EGA=dax.EGA16
# header bytes: 08 00 01 00 00 00 00 00  -> maybe (w=8? ...). Try reading width from header? hdr[0]=8.
# But coherent at ~16. Let me sweep 14-18 on full block, header 8.
d=dax.read_dax(os.path.join(GAME,"8X8D1.DAX"))[0]["data"][8:]
def strip(body,w,scale=3):
    px=[]
    for byte in body: px.append(byte>>4); px.append(byte&0xF)
    h=(len(px)+w-1)//w
    im=Image.new("RGB",(w,h),(25,25,35))
    for i,p in enumerate(px):
        if i//w<h: im.putpixel((i%w,i//w),EGA[p])
    return im.resize((w*scale,h*scale),Image.NEAREST)
widths=[14,15,16,17,18,20]
ims=[strip(d,w) for w in widths]
H=max(i.height for i in ims); W=sum(i.width for i in ims)+8*len(ims)
sheet=Image.new("RGB",(W,H+16),(50,50,60)); dr=ImageDraw.Draw(sheet); x=4
for w,im in zip(widths,ims):
    sheet.paste(im,(x,14)); dr.text((x,2),f"{w}",fill=(255,255,0)); x+=im.width+8
sheet.save(os.path.join(OUT,"_wallwidth.png")); print("saved", sheet.size)

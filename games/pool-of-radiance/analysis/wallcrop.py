import os, sys
sys.path.insert(0, r".\kit")
import dax
from PIL import Image
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\extracted_assets"
EGA=dax.EGA16
d=dax.read_dax(os.path.join(GAME,"8X8D1.DAX"))[0]["data"][8:]
# render several candidate widths of the FIRST 1024 bytes, side by side, scaled
def strip(body,w,scale=5):
    px=[]
    for byte in body: px.append(byte>>4); px.append(byte&0xF)
    h=(len(px)+w-1)//w
    im=Image.new("RGB",(w,h),(25,25,35))
    for i,p in enumerate(px):
        if i//w<h: im.putpixel((i%w,i//w),EGA[p])
    return im.resize((w*scale,h*scale),Image.NEAREST)
seg=d[:512]
widths=[8,16,24,32]
ims=[strip(seg,w) for w in widths]
from PIL import ImageDraw
H=max(i.height for i in ims); W=sum(i.width for i in ims)+10*len(ims)
sheet=Image.new("RGB",(W,H+16),(50,50,60)); dr=ImageDraw.Draw(sheet); x=5
for w,im in zip(widths,ims):
    sheet.paste(im,(x,14)); dr.text((x,2),f"w{w}",fill=(255,255,0)); x+=im.width+10
sheet.save(os.path.join(OUT,"_wallcrop.png")); print("saved _wallcrop.png", sheet.size)

import os, sys
sys.path.insert(0, r".\kit")
import dax
from PIL import Image
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\extracted_assets"
EGA=dax.EGA16
b=dax.read_dax(os.path.join(GAME,"8X8D1.DAX"))
print("8X8D1 blocks:")
for e in b:
    d=e["data"]; print(f"  id={e['id']:3d} unp={e['unpacked']:5d} hdr8={' '.join(f'{x:02X}' for x in d[:8])}")
# sweep widths on id1, linear 4bpp high-nibble
d=b[0]["data"][4:]   # skip 4-byte header
def lin(body,w,scale=2):
    px=[]
    for byte in body: px.append(byte>>4); px.append(byte&0xF)
    h=(len(px)+w-1)//w
    im=Image.new("RGB",(w,h),(20,20,30))
    for i,p in enumerate(px):
        if i//w<h: im.putpixel((i%w,i//w),EGA[p])
    return im.resize((w*scale,h*scale),Image.NEAREST)
widths=[16,32,48,56,64,88,112,176]
ims=[(w,lin(d,w)) for w in widths]
H=max(i.height for _,i in ims); from PIL import ImageDraw
sheet=Image.new("RGB",(sum(i.width for _,i in ims)+10*len(ims),H+18),(50,50,60))
dr=ImageDraw.Draw(sheet); x=5
for w,im in ims:
    sheet.paste(im,(x,16)); dr.text((x,2),f"w{w}",fill=(255,255,0)); x+=im.width+10
sheet.save(os.path.join(OUT,"_wall_sweep.png"))
print("saved _wall_sweep.png", sheet.size)

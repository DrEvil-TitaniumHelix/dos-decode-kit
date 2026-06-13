import os, sys
sys.path.insert(0, r".\kit")
import dax
from PIL import Image
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\extracted_assets"
EGA=dax.EGA16
for fn in ["CPIC1.DAX","CPIC2.DAX"]:
    b=dax.read_dax(os.path.join(GAME,fn))
    print(f"{fn}: {len(b)} blocks; ids={[e['id'] for e in b][:8]}")
    for e in b[:3]:
        d=e["data"]; print(f"  id={e['id']:3d} unp={e['unpacked']:5d} hdr={' '.join(f'{x:02X}' for x in d[:6])} w={d[0]}")
# render CPIC1 first few base sprites (id<128) at header width
b=dax.read_dax(os.path.join(GAME,"CPIC1.DAX"))
def render(d,scale=3):
    w=d[0]; body=d[4:]; px=[]
    for byte in body: px.append(byte>>4); px.append(byte&0xF)
    h=(len(px)+w-1)//w
    im=Image.new("RGB",(w,h),(20,20,30))
    for i,p in enumerate(px):
        if i//w<h: im.putpixel((i%w,i//w),EGA[p])
    return im.resize((w*scale,h*scale),Image.NEAREST)
bases=[e for e in b if e["id"]<128][:6]
ims=[render(e["data"]) for e in bases]
from PIL import ImageDraw
W=sum(i.width for i in ims)+10*len(ims); H=max(i.height for i in ims)+8
sheet=Image.new("RGB",(W,H),(50,50,60)); x=5
for im in ims: sheet.paste(im,(x,4)); x+=im.width+10
sheet.save(os.path.join(OUT,"_cpic_test.png"))
print("saved _cpic_test.png", sheet.size)

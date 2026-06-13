import os, sys
sys.path.insert(0, r".\kit")
import dax
from PIL import Image, ImageDraw
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\reproduction"
EGA=dax.EGA16
def head(d, w=44, scale=4):
    body=d[8:]; px=[]
    for byte in body: px.append(byte>>4); px.append(byte&0xF)
    h=(len(px)+w-1)//w
    im=Image.new("RGB",(w,h),(0,0,0))
    for i,p in enumerate(px):
        if i//w<h: im.putpixel((i%w,i//w),EGA[p])
    return im.resize((w*scale,h*scale),Image.NEAREST)
# render heads from HEAD1-4 (a few portraits)
ims=[]
for fn in ["HEAD1.DAX","HEAD2.DAX","HEAD3.DAX","HEAD4.DAX"]:
    p=os.path.join(GAME,fn)
    if os.path.exists(p):
        for e in dax.read_dax(p)[:2]:
            ims.append(head(e["data"]))
cw=max(i.width for i in ims)+8; ch=max(i.height for i in ims)+8
cols=min(8,len(ims))
s=Image.new("RGB",(cols*cw, ((len(ims)+cols-1)//cols)*ch),(40,40,55))
for i,im in enumerate(ims): s.paste(im,((i%cols)*cw+4,(i//cols)*ch+4))
s.save(os.path.join(OUT,"_real_heads.png")); print("saved _real_heads.png", s.size, len(ims),"portraits")

import os, sys
sys.path.insert(0, r".\kit")
import dax
from PIL import Image, ImageDraw
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\extracted_assets"
EGA=dax.EGA16
def render(body,w,scale=2,hskip=0):
    body=body[hskip:]; px=[]
    for byte in body: px.append(byte>>4); px.append(byte&0xF)
    h=(len(px)+w-1)//w
    im=Image.new("RGB",(w,h),(0,0,0))
    for i,p in enumerate(px):
        if i//w<h: im.putpixel((i%w,i//w),EGA[p])
    return im.resize((int(w*scale),int(h*scale)),Image.NEAREST)
# TITLE at 320 wide (full screen), try header skips 0/2/4
d=dax.read_dax(os.path.join(GAME,"TITLE.DAX"))[0]["data"]
print("TITLE len",len(d),"hdr",[hex(x) for x in d[:6]])
for hs in [0,2,4]:
    render(d,320,1,hs).save(os.path.join(OUT,f"_title_h{hs}.png"))
print("title rendered (h0/h2/h4)")
# BACPAC width sweep
b=dax.read_dax(os.path.join(GAME,"BACPAC.DAX"))[0]["data"]
print("BACPAC len",len(b),"hdr",[hex(x) for x in b[:6]])
ims=[render(b,w,3,8) for w in [16,24,32,48,64]]
W=sum(i.width for i in ims)+8*len(ims); H=max(i.height for i in ims)
sh=Image.new("RGB",(W,H+16),(50,50,60)); dr=ImageDraw.Draw(sh); x=4
for w,im in zip([16,24,32,48,64],ims): sh.paste(im,(x,14)); dr.text((x,2),str(w),fill=(255,255,0)); x+=im.width+8
sh.save(os.path.join(OUT,"_bacpac_sweep.png")); print("bacpac swept")

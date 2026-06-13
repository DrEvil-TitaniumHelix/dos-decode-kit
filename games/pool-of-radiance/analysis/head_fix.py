import os, sys
sys.path.insert(0, r".\kit")
import dax
from PIL import Image
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\extracted_assets"
EGA=dax.EGA16
d=dax.read_dax(os.path.join(GAME,"HEAD1.DAX"))[0]["data"]
# the banding: test if heads are INTERLACED (even rows then odd rows = EGA two-pass).
def render_interlaced(body, w, h, scale=5):
    px=[]
    for byte in body: px.append(byte>>4); px.append(byte&0xF)
    im=Image.new("RGB",(w,h),(0,0,0))
    half=h//2
    for srcrow in range(len(px)//w):
        # interlaced: first half = even rows, second half = odd rows
        if srcrow<half: dst=srcrow*2
        else: dst=(srcrow-half)*2+1
        if dst>=h: continue
        for c in range(w):
            im.putpixel((c,dst),EGA[px[srcrow*w+c]])
    return im.resize((w*scale,h*scale),Image.NEAREST)
def render_plain(body,w,h,scale=5):
    px=[]
    for byte in body: px.append(byte>>4); px.append(byte&0xF)
    im=Image.new("RGB",(w,h),(0,0,0))
    for i,p in enumerate(px):
        if i//w<h: im.putpixel((i%w,i//w),EGA[p])
    return im.resize((w*scale,h*scale),Image.NEAREST)
body=d[8:]
# heads ~ 44x40; compare plain vs interlaced
a=render_plain(body,44,40); b=render_interlaced(body,44,40)
sheet=Image.new("RGB",(a.width+b.width+20,max(a.height,b.height)+16),(50,50,60))
from PIL import ImageDraw; dr=ImageDraw.Draw(sheet)
sheet.paste(a,(4,14)); sheet.paste(b,(a.width+12,14)); dr.text((4,2),"plain",fill=(255,255,0)); dr.text((a.width+12,2),"de-interlaced",fill=(255,255,0))
sheet.save(os.path.join(OUT,"_head_fix.png")); print("saved _head_fix.png")

import os, sys
sys.path.insert(0, r".\kit")
import dax
from PIL import Image, ImageDraw
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\extracted_assets"
EGA=dax.EGA16
def render(d, w=None, scale=3):
    w=w or d[0]; body=d[4:]; px=[]
    for byte in body: px.append(byte>>4); px.append(byte&0xF)
    h=(len(px)+w-1)//w
    im=Image.new("RGB",(w,h),(0,0,0))
    for i,p in enumerate(px):
        if i//w<h: im.putpixel((i%w,i//w),EGA[p])
    return im.resize((w*scale,h*scale),Image.NEAREST)
for fn in ["HEAD1.DAX","BACPAC.DAX","PIC1.DAX","TITLE.DAX"]:
    p=os.path.join(GAME,fn)
    if not os.path.exists(p): print(fn,"missing"); continue
    b=dax.read_dax(p)
    print(f"{fn}: {len(b)} blocks; ids={[e['id'] for e in b][:6]}; sizes={[e['unpacked'] for e in b][:6]}; hdr0={[e['data'][0] for e in b][:6]}")
# render a sheet of HEAD1 + BACPAC + PIC1
def sheet(blocks, label):
    ims=[render(e["data"]) for e in blocks[:8]]
    if not ims: return None
    cw=max(i.width for i in ims)+8; ch=max(i.height for i in ims)+8
    cols=min(4,len(ims)); rows=(len(ims)+cols-1)//cols
    s=Image.new("RGB",(cols*cw, rows*ch),(50,50,60))
    for i,im in enumerate(ims): s.paste(im,((i%cols)*cw+4,(i//cols)*ch+4))
    s.save(os.path.join(OUT,f"_ui_{label}.png")); return s.size
for fn,lbl in [("HEAD1.DAX","heads"),("BACPAC.DAX","border"),("PIC1.DAX","pic")]:
    p=os.path.join(GAME,fn)
    if os.path.exists(p):
        sz=sheet(dax.read_dax(p), lbl); print(f"rendered _ui_{lbl}.png {sz}")

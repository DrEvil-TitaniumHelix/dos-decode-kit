import os, sys, base64, io
sys.path.insert(0, r".\kit")
import dax
from PIL import Image
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\extracted_assets"
EGA=dax.EGA16
d=dax.read_dax(os.path.join(GAME,"8X8D1.DAX"))[0]["data"][8:]
W=16
px=[]
for byte in d: px.append(byte>>4); px.append(byte&0xF)
rows=len(px)//W
best=None
for top in range(0, rows-16):
    cnt={}
    for r in range(top,top+16):
        for c in range(W): v=px[r*W+c]; cnt[v]=cnt.get(v,0)+1
    grey=cnt.get(7,0)+cnt.get(8,0)
    blk=cnt.get(0,0)
    bad=cnt.get(13,0)+cnt.get(9,0)+cnt.get(12,0)+cnt.get(6,0)+cnt.get(11,0)+cnt.get(10,0)+cnt.get(14,0)
    score=grey*2+blk-bad*3 + (40 if blk>8 and grey>20 else 0)
    if best is None or score>best[0]: best=(score,top)
top=best[1]
tile=Image.new("RGB",(16,16))
for r in range(16):
    for c in range(16): tile.putpixel((c,r),EGA[px[(top+r)*W+c]])
tile.resize((128,128),Image.NEAREST).save(os.path.join(OUT,"_walltex.png"))
buf=io.BytesIO(); tile.save(buf,"PNG")
url="data:image/png;base64,"+base64.b64encode(buf.getvalue()).decode()
open(os.path.join(OUT,"_walltex_url.txt"),"w").write(url)
print(f"masonry window row {top} score {best[0]}; url {len(url)} chars")

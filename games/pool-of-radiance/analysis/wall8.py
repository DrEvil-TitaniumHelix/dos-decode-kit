import os, sys
sys.path.insert(0, r".\kit")
import dax
from PIL import Image, ImageDraw
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\extracted_assets"
EGA=dax.EGA16
d=dax.read_dax(os.path.join(GAME,"8X8D1.DAX"))[0]["data"]
def render_lin(body,w,scale=6):
    px=[]
    for byte in body: px.append(byte>>4); px.append(byte&0xF)
    h=(len(px)+w-1)//w
    im=Image.new("RGB",(w,h),(25,25,35))
    for i,p in enumerate(px):
        if i//w<h: im.putpixel((i%w,i//w),EGA[p])
    return im.resize((w*scale,h*scale),Image.NEAREST)
def render_tiles(body,tw=8,th=8,scale=4):
    # 8x8 tiles, 4bpp linear, 32 bytes each, laid in a grid
    nt=len(body)//((tw*th)//2); cols=16; rows=(nt+cols-1)//cols
    im=Image.new("RGB",(cols*(tw+1)*scale,rows*(th+1)*scale),(40,40,55))
    for t in range(nt):
        tb=body[t*32:(t+1)*32]; px=[]
        for byte in tb: px.append(byte>>4); px.append(byte&0xF)
        bx=(t%cols)*(tw+1)*scale; by=(t//cols)*(th+1)*scale
        for i,p in enumerate(px):
            x=i%tw; y=i//tw
            for yy in range(scale):
                for xx in range(scale):
                    im.putpixel((bx+x*scale+xx,by+y*scale+yy),EGA[p])
    return im
# try header sizes 4 and 8, width-8 tall strip
for hs in [4,8]:
    im=render_lin(d[hs:], 8); im.save(os.path.join(OUT,f"_w8_strip_h{hs}.png"))
    print(f"width-8 strip (hdr {hs}): {im.size} -> _w8_strip_h{hs}.png")
# tile grid (hdr 8)
t=render_tiles(d[8:]); t.save(os.path.join(OUT,"_w8_tiles.png")); print("tiles:",t.size)

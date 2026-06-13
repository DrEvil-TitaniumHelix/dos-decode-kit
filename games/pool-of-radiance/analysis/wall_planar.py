import os, sys
sys.path.insert(0, r".\kit")
import dax
from PIL import Image, ImageDraw
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\extracted_assets"
EGA=dax.EGA16
def tile_planar(buf, off):
    # 8x8, 4 planes x 8 bytes; plane bit b of pixel -> color
    px=[[0]*8 for _ in range(8)]
    for pl in range(4):
        for row in range(8):
            byte=buf[off+pl*8+row]
            for col in range(8):
                if byte & (0x80>>col): px[row][col]|=(1<<pl)
    return px
def tile_planar_interleaved(buf, off):
    # per-row: 4 plane-bytes interleaved (b0 b1 b2 b3 per row)
    px=[[0]*8 for _ in range(8)]
    for row in range(8):
        for pl in range(4):
            byte=buf[off+row*4+pl]
            for col in range(8):
                if byte&(0x80>>col): px[row][col]|=(1<<pl)
    return px
def sheet(data, fn, mode):
    ntile=len(data)//32
    cols=16; rows=(ntile+cols-1)//cols; cell=8*3
    im=Image.new("RGB",(cols*cell+cols, rows*cell+rows),(40,40,55))
    for t in range(ntile):
        px=(tile_planar if mode=="block" else tile_planar_interleaved)(data,t*32)
        tx=(t%cols)*(cell+1); ty=(t//cols)*(cell+1)
        for r in range(8):
            for c in range(8):
                col=EGA[px[r][c]]
                for yy in range(3):
                    for xx in range(3):
                        im.putpixel((tx+c*3+xx,ty+r*3+yy),col)
    im.save(os.path.join(OUT,fn)); return ntile,im.size
for mode in ["block","interleaved"]:
    d=dax.read_dax(os.path.join(GAME,"8X8D1.DAX"))[0]["data"]
    n,sz=sheet(d, f"_wall_planar_{mode}.png", mode)
    print(f"{mode}: {n} tiles -> _wall_planar_{mode}.png {sz}")

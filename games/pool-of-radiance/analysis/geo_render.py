import os, struct
from PIL import Image, ImageDraw
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT=r".\games\pool-of-radiance\extracted_assets"
def parse(b):
    hdr=struct.unpack_from("<H",b,0)[0]; n=hdr//9; es=[]; pos=2
    for _ in range(n):
        eid,off,unp,pk=struct.unpack_from("<BIHH",b,pos); es.append(dict(id=eid,off=off,unp=unp,pk=pk)); pos+=9
    data=b[2+hdr:]
    for e in es: e["raw"]=data[e["off"]:e["off"]+e["pk"]]
    return es
def decomp(src):
    out=bytearray(); i=0
    while i<len(src):
        c=src[i]; i+=1
        if c<0x80: out+=src[i:i+c+1]; i+=c+1
        else: out+=bytes([src[i]])*(256-c); i+=1
    return bytes(out)
def render_map(d, cell=14):
    grid=d[2:2+1024]   # skip 2-byte header
    N=32
    im=Image.new("RGB",(N*cell+1,N*cell+1),(20,20,25))
    dr=ImageDraw.Draw(im)
    for idx,byte in enumerate(grid):
        x=idx%N; y=idx//N
        south=byte>>4; east=byte&0xF
        px,py=x*cell,y*cell
        col_s=(230,230,120) if south else None
        col_e=(120,200,230) if east else None
        if south: dr.line([(px,py+cell),(px+cell,py+cell)],fill=(220,220,140),width=2)
        if east:  dr.line([(px+cell,py),(px+cell,py+cell)],fill=(150,200,240),width=2)
    return im
# render the first block of several GEO files into a contact sheet of maps
files=[f"GEO{i}.DAX" for i in range(1,9)]
maps=[]
for fn in files:
    p=os.path.join(GAME,fn)
    if not os.path.exists(p): continue
    es=parse(open(p,"rb").read())
    d=decomp(es[0]["raw"])
    if len(d)>=1026:
        im=render_map(d); maps.append((f"{fn}#{es[0]['id']}",im))
# montage 4 cols
cols=4; cw=max(i.width for _,i in maps)+8; ch=max(i.height for _,i in maps)+18
rows=(len(maps)+cols-1)//cols
sheet=Image.new("RGB",(cols*cw,rows*ch),(40,40,50)); dr=ImageDraw.Draw(sheet)
for idx,(nm,im) in enumerate(maps):
    x=(idx%cols)*cw+4; y=(idx//cols)*ch+16
    sheet.paste(im,(x,y)); dr.text((x,(idx//cols)*ch+2),nm,fill=(255,255,180))
sheet.save(os.path.join(OUT,"GEO_dungeon_maps.png"))
print("rendered", len(maps), "GEO maps ->", sheet.size)

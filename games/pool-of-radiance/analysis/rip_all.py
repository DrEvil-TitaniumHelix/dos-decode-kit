import os, struct, glob
from PIL import Image
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT=r".\games\pool-of-radiance\extracted_assets"
EGA=[(0,0,0),(0,0,170),(0,170,0),(0,170,170),(170,0,0),(170,0,170),(170,85,0),(170,170,170),
     (85,85,85),(85,85,255),(85,255,85),(85,255,255),(255,85,85),(255,85,255),(255,255,85),(255,255,255)]
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
def render(d,scale=3):
    w=max(1,d[0]); body=d[4:]
    px=[]
    for byte in body: px.append(byte>>4); px.append(byte&0xF)
    h=max(1,(len(px)+w-1)//w)
    im=Image.new("RGB",(w,h),(0,0,0))
    for i,p in enumerate(px):
        if i//w<h: im.putpixel((i%w,i//w),EGA[p])
    return im.resize((w*scale,h*scale),Image.NEAREST)
def sheet(es,cols=16):
    imgs=[render(decomp(e["raw"])) for e in es]
    cw=max(i.width for i in imgs)+6; ch=max(i.height for i in imgs)+6
    rows=(len(imgs)+cols-1)//cols
    s=Image.new("RGB",(cols*cw,rows*ch),(45,45,55))
    for idx,im in enumerate(imgs):
        s.paste(im,((idx%cols)*cw+3,(idx//cols)*ch+3))
    return s,len(imgs)
groups={"CHEAD":["CHEAD.DAX"],"BODIES":[f"BODY{i}.DAX" for i in range(1,9)],
        "COMSPR":["COMSPR.DAX"],"CPIC":[f"CPIC{i}.DAX" for i in range(1,9)],
        "TILES_8X8":[f"8X8D{i}.DAX" for i in range(1,9)]}
for gname,files in groups.items():
    allblk=[]
    for fn in files:
        p=os.path.join(GAME,fn)
        if os.path.exists(p): allblk+=parse(open(p,"rb").read())
    if not allblk: continue
    s,n=sheet(allblk)
    s.save(os.path.join(OUT,f"{gname}_sheet.png"))
    print(f"{gname:12s}: {n:4d} blocks -> {gname}_sheet.png  {s.size}")

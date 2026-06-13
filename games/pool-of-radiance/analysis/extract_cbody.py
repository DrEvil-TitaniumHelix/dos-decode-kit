import os, struct
from PIL import Image, ImageDraw
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
def render(d, scale=3):
    w=d[0]            # header word0 = width in px (verified visually)
    body=d[4:]
    px=[]
    for byte in body:
        px.append(byte>>4); px.append(byte&0xF)
    h=(len(px)+w-1)//w
    im=Image.new("RGB",(w,h),(0,0,0))
    for i,p in enumerate(px):
        if i//w<h: im.putpixel((i%w,i//w),EGA[p])
    return im.resize((w*scale,h*scale),Image.NEAREST)
b=open(os.path.join(GAME,"CBODY.DAX"),"rb").read(); es=parse(b)
imgs=[(e["id"],render(decomp(e["raw"]))) for e in es]
cols=16; cw=max(i.width for _,i in imgs)+6; ch=max(i.height for _,i in imgs)+6
rows=(len(imgs)+cols-1)//cols
sheet=Image.new("RGB",(cols*cw, rows*ch),(50,50,60))
for idx,(eid,im) in enumerate(imgs):
    x=(idx%cols)*cw+3; y=(idx//cols)*ch+3
    sheet.paste(im,(x,y))
sheet.save(os.path.join(OUT,"CBODY_all_combat_sprites.png"))
print("CBODY: extracted", len(imgs), "combat sprites ->", sheet.size)

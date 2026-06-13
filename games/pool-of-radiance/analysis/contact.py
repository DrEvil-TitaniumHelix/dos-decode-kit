import os, struct
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
def render(body,w,scale=4):
    px=[]
    for byte in body:
        px.append(byte>>4); px.append(byte&0xF)
    h=(len(px)+w-1)//w
    im=Image.new("RGB",(w,h),(30,30,30))
    for i,p in enumerate(px):
        if i//w<h: im.putpixel((i%w,i//w),EGA[p])
    return im.resize((w*scale,h*scale),Image.NEAREST)
b=open(os.path.join(GAME,"CBODY.DAX"),"rb").read(); es=parse(b)
d0=decomp(es[0]["raw"])[4:]   # skip 4-byte header
widths=[12,14,16,20,24]
ims=[render(d0,w) for w in widths]
H=max(i.height for i in ims); W=sum(i.width for i in ims)+10*len(ims)
sheet=Image.new("RGB",(W,H+20),(60,60,60)); x=5
from PIL import ImageDraw
dr=ImageDraw.Draw(sheet)
for w,im in zip(widths,ims):
    sheet.paste(im,(x,15)); dr.text((x,2),f"w={w}",fill=(255,255,0)); x+=im.width+10
sheet.save(os.path.join(OUT,"_contact_cbody.png"))
print("saved", os.path.join(OUT,"_contact_cbody.png"), sheet.size)

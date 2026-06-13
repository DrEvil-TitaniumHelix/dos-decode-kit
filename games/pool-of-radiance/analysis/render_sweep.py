import os, struct
from PIL import Image
GAME = r".\games\pool-of-radiance\extracted\poolrad"
OUT  = r".\games\pool-of-radiance\extracted_assets"
os.makedirs(OUT, exist_ok=True)
EGA = [(0,0,0),(0,0,170),(0,170,0),(0,170,170),(170,0,0),(170,0,170),(170,85,0),(170,170,170),
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
def to_img(px, w, hdr_skip=4):
    body=px[hdr_skip:]
    pixels=[]
    for byte in body:
        pixels.append(byte>>4); pixels.append(byte&0xF)   # 4bpp, high nibble first
    h=(len(pixels)+w-1)//w
    im=Image.new("RGB",(w,h),(40,40,40))
    for idx,p in enumerate(pixels):
        x=idx%w; y=idx//w
        if y<h: im.putpixel((x,y),EGA[p])
    return im
# CBODY: 128 identical-size blocks => the 128 combat monster bodies. header[0]=24 -> guess width.
b=open(os.path.join(GAME,"CBODY.DAX"),"rb").read(); es=parse(b)
d0=decomp(es[0]["raw"])
print("CBODY block0 dims-header:", d0[0],d0[1],d0[2],d0[3], " bodylen", len(d0)-4)
# sweep widths on first body
for w in [16,24,28,32,48,56]:
    im=to_img(d0,w); im=im.resize((im.width*4,im.height*4),Image.NEAREST)
    im.save(os.path.join(OUT,f"_sweep_cbody_w{w}.png"))
print("saved CBODY width sweeps")
# header says first word=24 (0x18). width in pixels=24 -> 4bpp=12 bytes/row. (305-4)=301 /12=25.08. try w such that divides.
rem=len(d0)-4
print("rem=",rem,"factor candidates (rem/bytesPerRow):",[(w, rem/((w+1)//2 if False else w/2)) for w in [16,24,28,32,48]])

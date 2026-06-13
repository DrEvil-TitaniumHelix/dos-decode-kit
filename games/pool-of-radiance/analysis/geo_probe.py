import os, struct
GAME=r".\games\pool-of-radiance\extracted\poolrad"
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
def hx(b,n=80):
    o=[]
    for i in range(0,min(len(b),n),16):
        chunk=b[i:i+16]
        o.append(f"  {i:04X}  "+" ".join(f"{x:02X}" for x in chunk)+"   "+"".join(chr(x) if 32<=x<127 else '.' for x in chunk))
    return "\n".join(o)
for fn in ["GEO1.DAX","GEO3.DAX"]:
    b=open(os.path.join(GAME,fn),"rb").read(); es=parse(b)
    print(f"\n=== {fn}: ids={[e['id'] for e in es]} ===")
    for e in es:
        d=decomp(e["raw"])
        print(f" -- block id={e['id']} unp={e['unp']} len={len(d)}; sqrt={len(d)**0.5:.1f}")
        print(hx(d,64))
        # GEO maps in Gold Box are typically 16x16 grids. Check factorizations.
        for sq in [16,32,8]:
            if len(d)%sq==0: print(f"    {len(d)} = {sq} x {len(d)//sq}")

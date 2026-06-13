import os, struct, glob
GAME = r".\games\pool-of-radiance\extracted\poolrad"
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
        else:
            cnt=256-c; out+=bytes([src[i]])*cnt; i+=1
    return bytes(out)
for fn in ["CHEAD.DAX","CBODY.DAX","8X8D1.DAX","BODY1.DAX"]:
    b=open(os.path.join(GAME,fn),"rb").read(); es=parse(b)
    print(f"\n=== {fn}: {len(es)} blocks ===")
    for e in es[:4]:
        d=decomp(e["raw"])
        first=' '.join(f'{x:02X}' for x in d[:8])
        print(f" id={e['id']:3d} unp={e['unp']:5d}; first8={first}")
        if len(d)>=4:
            a,b2,c2,e2=d[0],d[1],d[2],d[3]
            rem=len(d)-4
            hits=[]
            for (W,H) in [(c2,e2),(a,b2),(b2,a),(e2,c2)]:
                bpr=(W*H)//2
                if bpr and rem % bpr==0:
                    hits.append(f"{W}x{H}->{rem//bpr}f")
            print(f"      hdr[{a},{b2},{c2},{e2}] rem={rem}  fits: {hits}")

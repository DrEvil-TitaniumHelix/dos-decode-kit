import os, struct, glob
GAME = r".\games\pool-of-radiance\extracted\poolrad"

def parse(b):
    hdr = struct.unpack_from("<H", b, 0)[0]; n = hdr // 9
    es=[]; pos=2
    for _ in range(n):
        eid,off,unp,pk = struct.unpack_from("<BIHH", b, pos); es.append(dict(id=eid,off=off,unp=unp,pk=pk)); pos+=9
    data=b[2+hdr:]
    for e in es: e["raw"]=data[e["off"]:e["off"]+e["pk"]]
    return es

def dax_decompress(src, target=None):
    out=bytearray(); i=0
    while i < len(src):
        c=src[i]; i+=1
        if c < 0x80:
            run=c+1; out+=src[i:i+run]; i+=run
        else:
            cnt=256-c
            if i>=len(src): break
            out+=bytes([src[i]])*cnt; i+=1
        if target is not None and len(out)>=target: break
    return bytes(out), i

allfiles=sorted(glob.glob(os.path.join(GAME,"*.DAX")))
exact=0; total=0; consumed_ok=0; bad=[]
for p in allfiles:
    b=open(p,"rb").read()
    for e in parse(b):
        out,cons=dax_decompress(e["raw"], e["unp"])
        total+=1
        lenok=(len(out)==e["unp"])
        if lenok: exact+=1
        else: bad.append((os.path.basename(p),e["id"],len(out),e["unp"]))
print(f"DAX RLE decode (c<0x80: copy c+1 literals; c>=0x80: repeat next byte 256-c times)")
print(f"EXACT unpacked-size match: {exact}/{total} blocks")
if bad:
    print(f"misses ({len(bad)}):"); [print("  ",x) for x in bad[:20]]

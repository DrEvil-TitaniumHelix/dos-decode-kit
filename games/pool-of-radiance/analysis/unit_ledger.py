import struct, json
from collections import Counter
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ovr=open(GAME+r"\GAME.OVR","rb").read()
ex=open(GAME+r"\START.EXE","rb").read()
segs=json.load(open("overlay_segmap.json"))
md=Cs(CS_ARCH_X86,CS_MODE_16)

# functions = 55 89 E5 prologues
def find_all(b,pat):
    o=[];i=b.find(pat)
    while i!=-1:o.append(i);i=b.find(pat,i+1)
    return o
funcs=find_all(ovr,b"\x55\x89\xe5")
# near-call counts
calls=Counter();i=0
while i<len(ovr)-3:
    if ovr[i]==0xE8:
        rel=struct.unpack_from("<h",ovr,i+1)[0];t=i+3+rel
        if 0<=t<len(ovr):calls[t]+=1
    i+=1

# assign funcs to units by ovr file-offset range
def unit_of(off):
    for s in segs:
        if s["ovr_off"]<=off<s["ovr_off"]+s["csize"]: return s
    return None
unit_funcs=Counter()
for f in funcs:
    u=unit_of(f)
    if u: unit_funcs[u["seg"]]+=1

# public entry points per unit: read the entry stubs in START.EXE after each seg header
def entry_offsets(s):
    # entries are the run of CD 3F <w off> 00 right after a small header gap; the header is at s['file'].
    # entry stubs in TP overlays live in the stub segment starting at s['file']; the first CD3F is the seg trap,
    # subsequent CD 3F xx xx 00 (nonzero off) are entry thunks. Collect offsets.
    outs=[]; pos=s["file"]
    # scan forward up to nentry*5+32 bytes for CD3F with nonzero word
    end=pos+ s["nent"]*8 + 64
    p=pos
    while p<end-5 and len(outs)<s["nent"]:
        if ex[p]==0xCD and ex[p+1]==0x3F:
            w=struct.unpack_from("<H",ex,p+2)[0]
            if w!=0: outs.append(w)
            p+=5
        else: p+=1
    return outs

print(f"{'unit':>6}{'ovr_off':>9}{'codesz':>8}{'#funcs':>7}{'#entry':>7}   role-hint(entry offsets)")
segs.sort(key=lambda s:-s["nent"])
ledger=[]
for s in segs:
    eo=entry_offsets(s)
    row=dict(unit=s["seg"],ovr_off=s["ovr_off"],csize=s["csize"],nfuncs=unit_funcs.get(s["seg"],0),nentry=s["nent"],entries=eo)
    ledger.append(row)
    print(f"  0x{s['seg']:04X}{s['ovr_off']:9d}{s['csize']:8d}{unit_funcs.get(s['seg'],0):7d}{s['nent']:7d}   {eo[:6]}")
json.dump(ledger,open("unit_ledger.json","w"),indent=1)
print(f"\nfuncs assigned: {sum(unit_funcs.values())}/{len(funcs)}")

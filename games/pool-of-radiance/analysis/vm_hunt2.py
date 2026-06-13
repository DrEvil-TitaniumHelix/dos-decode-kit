import struct, json
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ov=open(GAME+r"\GAME.OVR","rb").read()
md=Cs(CS_ARCH_X86,CS_MODE_16)
segs={s["seg"]:s for s in json.load(open("overlay_segmap.json"))}
def unit_of(off):
    for s in segs.values():
        if s["ovr_off"]<=off<s["ovr_off"]+s["csize"]: return s
    return None
# Scan for jump TABLES: runs of >=16 consecutive u16 that are all valid offsets within
# their containing unit's code size (i.e., < csize). These are dispatch tables.
print("candidate jump tables (>=20 consecutive in-unit code offsets):")
i=0
found=[]
while i < len(ov)-2:
    u=unit_of(i)
    if not u: i+=1; continue
    lo=u["ovr_off"]; hi=u["csize"]
    # count run of u16 in [4, csize)
    j=i; run=0
    while j+2<=len(ov):
        v=struct.unpack_from("<H",ov,j)[0]
        if 4<=v<hi: run+=1; j+=2
        else: break
    if run>=20:
        found.append((i,run,u["seg"]))
        i=j
    else:
        i+=1
for off,run,seg in found[:20]:
    print(f"  @0x{off:05X} unit 0x{seg:04X}: {run} entries (table of {run} handlers?)")
# the ECL VM table should have ~40 entries. show those near 40.
print("\ntables with 30-60 entries (ECL opcode count ~40):")
for off,run,seg in found:
    if 30<=run<=60: print(f"  @0x{off:05X} unit 0x{seg:04X}: {run} entries  first8={[hex(struct.unpack_from('<H',ov,off+k*2)[0]) for k in range(8)]}")

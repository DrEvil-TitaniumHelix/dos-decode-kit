from capstone import Cs, CS_ARCH_X86, CS_MODE_16
import struct
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ov=open(GAME+r"\GAME.OVR","rb").read()
md=Cs(CS_ARCH_X86, CS_MODE_16)
def show(buf,base,label,maxn=34):
    print(f"\n=== {label} @0x{base:05X} ===")
    n=0
    for ins in md.disasm(buf,base):
        print(f"  {ins.address:06X}: {' '.join(f'{b:02X}' for b in ins.bytes):<20} {ins.mnemonic:7s} {ins.op_str}")
        n+=1
        if n>=maxn: break
# the 140x hot routine
show(ov[0x2B04A:0x2B04A+110],0x2B04A,"HOTTEST routine (140 callers)")
show(ov[0x278DB:0x278DB+90],0x278DB,"2nd hot (33 callers)")
show(ov[0x0C7F2:0x0C7F2+90],0x0C7F2,"3rd hot (22 callers)")

# START.EXE: where's the video code? find A000/B800 immediates
ex=open(GAME+r"\START.EXE","rb").read()
for seg,name in [(0xA000,"EGA A000"),(0xB800,"text B800")]:
    pat=bytes([0xB8,seg&0xFF,seg>>8]); i=ex.find(pat); locs=[]
    while i!=-1: locs.append(i); i=ex.find(pat,i+1)
    print(f"\nSTART.EXE mov ax,{seg:04X}h ({name}): {len(locs)} sites; first {[hex(x) for x in locs[:5]]}")

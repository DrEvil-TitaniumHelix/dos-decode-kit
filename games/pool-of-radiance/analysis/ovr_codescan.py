import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ov=open(GAME+r"\GAME.OVR","rb").read()
md=Cs(CS_ARCH_X86, CS_MODE_16)

# Parse FBOV header region
print("FBOV header first 64:", " ".join(f"{x:02X}" for x in ov[:64]))
# u32 after 'FBOV' often = file size or table offset
val=struct.unpack_from("<I",ov,4)[0]
print(f"dword@4 = {val} (0x{val:X}); file len={len(ov)}")

# Code-density scan: slide a window, measure fraction decoded as common x86 ops
COMMON={'mov','push','pop','call','ret','retf','jmp','je','jne','add','sub','cmp','test',
        'lea','xor','or','and','int','inc','dec','les','les','les'}
def density(buf):
    ok=0; tot=0
    for ins in md.disasm(buf,0):
        tot+=1
        if ins.mnemonic in COMMON: ok+=1
    return ok/tot if tot else 0, tot
W=512
print("\noffset    common%  insns   (code-like regions >0.55)")
regions=[]
for off in range(0,len(ov)-W,W):
    d,n=density(ov[off:off+W])
    if d>0.55 and n>40:
        regions.append(off)
# compress contiguous
if regions:
    runs=[]; s=regions[0]; p=regions[0]
    for o in regions[1:]:
        if o-p<=W: p=o
        else: runs.append((s,p+W)); s=o; p=o
    runs.append((s,p+W))
    for a,b in runs:
        print(f"  CODE 0x{a:05X}-0x{b:05X}  ({b-a} bytes)")
    # disassemble the start of the first big code run
    a0=runs[0][0]
    print(f"\n=== disasm @ 0x{a0:05X} (first code run) ===")
    for ins in list(md.disasm(ov[a0:a0+120],a0))[:30]:
        print(f"  {ins.address:06X}: {ins.mnemonic:7s} {ins.op_str}")
else:
    print("  no high-density code window found at W=512")

import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ov=open(GAME+r"\GAME.OVR","rb").read()
ex=open(GAME+r"\START.EXE","rb").read()
md=Cs(CS_ARCH_X86, CS_MODE_16); md.detail=True

def dis_file(buf, addr, n=160, stop=True):
    out=[]
    for ins in md.disasm(buf[addr:addr+n], addr):
        out.append(f"  {ins.address:06X}: "+" ".join(f"{b:02X}" for b in ins.bytes).ljust(16)+f"{ins.mnemonic} {ins.op_str}")
        if stop and ins.mnemonic in ("ret","retf"): break
        if ins.address-addr>n-12: break
    return "\n".join(out)

# resident helper seg:off -> START.EXE file offset 0x200 + seg*16 + off
def resident(seg,off): return 0x200+seg*16+off

# 0x2b helpers seen: 0x25 (get-byte+advance), 0x2a (sub-pc?), 0x4d, 0x5c, 0x8e
for name,seg,off in [("0x2b:0x25",0x2b,0x25),("0x2b:0x2a",0x2b,0x2a),("0x2b:0x4d",0x2b,0x4d),
                     ("0x2b:0x5c",0x2b,0x5c),("0x2b:0x8e",0x2b,0x8e)]:
    fo=resident(seg,off)
    print(f"==== resident {name} @file 0x{fo:X} ====")
    print(dis_file(ex,fo,140))
    print()

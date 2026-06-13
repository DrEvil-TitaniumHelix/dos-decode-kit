import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ov=open(GAME+r"\GAME.OVR","rb").read()
ex=open(GAME+r"\START.EXE","rb").read()
md=Cs(CS_ARCH_X86, CS_MODE_16); md.detail=True

def resident(seg,off):
    return 0x200 + seg*16 + off

def dis(addr, n=120, stop_at_ret=True):
    out=[]
    code=ov[addr:addr+n]
    for ins in md.disasm(code, addr):
        line=f"  {ins.address:06X}: "+" ".join(f"{b:02X}" for b in ins.bytes).ljust(20)+f"{ins.mnemonic} {ins.op_str}"
        # annotate far calls
        if ins.mnemonic=="lcall":
            ops=ins.op_str
            line+="   ; lcall"
        out.append(line)
        if stop_at_ret and ins.mnemonic in ("ret","retf"):
            break
        if ins.address-addr>n-10: break
    return "\n".join(out)

handlers={0x10:0x16DA,0x11:0x174F,0x13:0x17E5,0x14:0x1833,0x15:0x1C4E,0x16:0x1898,0x17:0x19BA}
for op,a in handlers.items():
    print(f"==== opcode 0x{op:02X} handler @0x{a:04X} ====")
    print(dis(a, 200))
    print()

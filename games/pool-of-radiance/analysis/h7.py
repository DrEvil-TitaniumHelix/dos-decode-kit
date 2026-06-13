from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ex=open(GAME+r"\START.EXE","rb").read()
md=Cs(CS_ARCH_X86, CS_MODE_16)
def resident(seg,off): return 0x200+seg*16+off
def dis(buf,addr,n,stop=True):
    out=[]
    for ins in md.disasm(buf[addr:addr+n],addr):
        out.append(f"  {ins.address:06X}: "+" ".join(f'{b:02X}' for b in ins.bytes).ljust(16)+f"{ins.mnemonic} {ins.op_str}")
        if stop and ins.mnemonic in ("ret","retf"): break
        if ins.address-addr>n-12: break
    return "\n".join(out)
for nm,seg,off in [("0x709:0x768",0x709,0x768),("0xba:0x1073",0xba,0x1073),("0x3d5:0x3e",0x3d5,0x3e),
                   ("0x3c5:0x3e",0x3c5,0x3e),("0x3c5:0x43",0x3c5,0x43)]:
    fo=resident(seg,off)
    print(f"==== {nm} @file 0x{fo:X} ====")
    print(dis(ex,fo,0xA0))
    print()

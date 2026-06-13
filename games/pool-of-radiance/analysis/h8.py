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
for nm,seg,off in [("0xba:0x27d9 (combat?)",0xba,0x27d9),("0xba:0x767",0xba,0x767),
                   ("0xba:0x1073",0xba,0x1073)]:
    fo=resident(seg,off)
    print(f"==== {nm} @file 0x{fo:X} ====")
    print(dis(ex,fo,0x60))
    print()
# 0x2b:0x8e int 0x3f stub bytes
fo=resident(0x2b,0x8e); print("0x2b:0x8e raw:"," ".join(f"{b:02X}" for b in ex[fo:fo+8]))

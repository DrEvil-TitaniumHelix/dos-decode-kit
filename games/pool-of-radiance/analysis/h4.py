from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ov=open(GAME+r"\GAME.OVR","rb").read()
ex=open(GAME+r"\START.EXE","rb").read()
md=Cs(CS_ARCH_X86, CS_MODE_16)
def dis(buf,addr,n,stop=True):
    out=[]
    for ins in md.disasm(buf[addr:addr+n],addr):
        out.append(f"  {ins.address:06X}: "+" ".join(f'{b:02X}' for b in ins.bytes).ljust(16)+f"{ins.mnemonic} {ins.op_str}")
        if stop and ins.mnemonic in ("ret","retf"): break
        if ins.address-addr>n-12: break
    return "\n".join(out)
# rest of 0x15 (from 0x1D0E) and 0x17 (from 0x1A7C)
print("==== 0x15 cont @0x1D0E ====")
print(dis(ov,0x1D0E,0x140))
print("\n==== 0x17 cont @0x1A7C ====")
print(dis(ov,0x1A7C,0x120))

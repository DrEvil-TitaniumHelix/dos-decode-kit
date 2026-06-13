from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ov=open(GAME+r"\GAME.OVR","rb").read()
md=Cs(CS_ARCH_X86, CS_MODE_16)
def dis(buf,addr,n,stop=True):
    out=[]
    for ins in md.disasm(buf[addr:addr+n],addr):
        out.append(f"  {ins.address:06X}: "+" ".join(f'{b:02X}' for b in ins.bytes).ljust(16)+f"{ins.mnemonic} {ins.op_str}")
        if stop and ins.mnemonic in ("ret","retf"): break
        if ins.address-addr>n-12: break
    return "\n".join(out)
# Find handlers that write [0x49ed] (=PC) -> GOTO/CALL. Already: 0x17E5(0x13 RET), 0x16DA? no.
# Look at 0x0A(0x1026), 0x0B(0x1196), 0x0C(0x10FA), 0x0D(0x155D) for IF/GOTO/CALL
for op,a in [(0x0A,0x1026),(0x0C,0x10FA),(0x0B,0x1196),(0x0D,0x155D),(0x09,0x0FD8),(0x08,0x0F7A)]:
    print(f"==== 0x{op:02X} @0x{a:04X} ====")
    print(dis(ov,a,0xA0))
    print()

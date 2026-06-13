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
# PRINT-TEXT candidate 0x00, GOTO candidate, and 0x12 path of 0x174F (already seen, branches on 0x6f7f==0x11)
# opcode 0x12 reuses 0x174F handler; that handler checks [0x6f7f]==0x11. So 0x12 falls to else-branch.
# Print-text 0x00 @0xD47
print("==== 0x00 @0x0D47 (print-text candidate) ====")
print(dis(ov,0xD47,0x120))
# 0x0E @0x159C, 0x0F @0x1697 for GOTO/branch baseline
print("\n==== 0x0E @0x159C ====")
print(dis(ov,0x159C,0xC0))
print("\n==== 0x0F @0x1697 ====")
print(dis(ov,0x1697,0xB0))

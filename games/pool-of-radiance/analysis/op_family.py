from capstone import Cs, CS_ARCH_X86, CS_MODE_16
OVR = r".\games\pool-of-radiance\extracted\poolrad\GAME.OVR"
data = open(OVR,'rb').read()
md = Cs(CS_ARCH_X86, CS_MODE_16)
def disasm(addr, length=600, n=80, label=""):
    print(f"\n=== {label} @0x{addr:04X} ===")
    cnt=0
    for ins in md.disasm(data[addr:addr+length], addr):
        print(f"  0x{ins.address:04X}: {ins.mnemonic:7s} {ins.op_str}")
        cnt+=1
        if cnt>=n: break
        if ins.mnemonic in ('ret','retf'): break
# comparison family - these set [0x6f78..6f7d]?
disasm(0x174F, label="op0x11-12 handler")
disasm(0x17E5, label="op0x13 handler")
disasm(0x1C4E, label="op0x15 handler")
disasm(0x10FA, label="op0x0C handler (TEST?)")

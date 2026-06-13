from capstone import Cs, CS_ARCH_X86, CS_MODE_16
OVR = r".\games\pool-of-radiance\extracted\poolrad\GAME.OVR"
data = open(OVR,'rb').read()
md = Cs(CS_ARCH_X86, CS_MODE_16)
def disasm(addr, length=600, n=120, label=""):
    print(f"\n=== {label} @0x{addr:04X} ===")
    cnt=0
    for ins in md.disasm(data[addr:addr+length], addr):
        print(f"  0x{ins.address:04X}: {ins.mnemonic:7s} {ins.op_str}")
        cnt+=1
        if cnt>=n: break
        if ins.mnemonic in ('ret','retf'): break
# Calibration set: known structural opcodes from the table to anchor semantics
# 0x00 first handler (likely a common one), 0x14 (0x1833), 0x20(0x1917), 0x2A(0x1BA4)
disasm(0x0D47, label="op0x00 handler")
disasm(0x1833, label="op0x14 handler")
disasm(0x1917, label="op0x20 handler (=ECL filename builder per locate)")

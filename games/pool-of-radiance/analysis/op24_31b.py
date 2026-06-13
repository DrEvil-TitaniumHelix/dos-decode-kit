from capstone import Cs, CS_ARCH_X86, CS_MODE_16
OVR = r".\games\pool-of-radiance\extracted\poolrad\GAME.OVR"
data = open(OVR,'rb').read()
md = Cs(CS_ARCH_X86, CS_MODE_16)

def disasm(addr, length=400, n=200):
    cnt=0
    for ins in md.disasm(data[addr:addr+length], addr):
        print(f"  0x{ins.address:04X}: {ins.mnemonic:7s} {ins.op_str}")
        cnt+=1
        if cnt>=n: break
        if ins.mnemonic in ('ret','retf'):
            break

print("##### opcode 0x1E (dec 30) -> handler 0x217B (full) #####")
disasm(0x217B, length=500, n=200)

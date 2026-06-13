import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_16

OVR = r".\games\pool-of-radiance\extracted\poolrad\GAME.OVR"
data = open(OVR,'rb').read()
md = Cs(CS_ARCH_X86, CS_MODE_16)
md.detail = False

def disasm(addr, n=80, stop_at_ret=True):
    print(f"=== handler @0x{addr:04X} ===")
    cnt=0
    for ins in md.disasm(data[addr:addr+400], addr):
        print(f"  0x{ins.address:04X}: {ins.mnemonic:7s} {ins.op_str}")
        cnt+=1
        if cnt>=n: break
        if stop_at_ret and ins.mnemonic in ('ret','retf'):
            break

handlers = {
  0x18:0x1898, 0x19:0x1898, 0x1A:0x1898, 0x1B:0x1898,
  0x1C:0x1FA3, 0x1D:0x200C, 0x1E:0x217B,
}
done=set()
for op,h in handlers.items():
    if h in done:
        print(f"# opcode 0x{op:02X} shares handler 0x{h:04X}")
        continue
    done.add(h)
    print(f"\n##### opcode 0x{op:02X} (dec {op}) -> handler 0x{h:04X} #####")
    disasm(h, n=120)

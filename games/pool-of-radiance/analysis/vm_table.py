import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ov=open(GAME+r"\GAME.OVR","rb").read()
md=Cs(CS_ARCH_X86,CS_MODE_16)
print("=== ECL dispatcher disasm (0x2DDC0..0x2DE00) ===")
for ins in md.disasm(ov[0x2DDC0:0x2DE00],0x2DDC0):
    print(f"  {ins.address:06X}: {' '.join(f'{b:02X}' for b in ins.bytes):<14} {ins.mnemonic:6s} {ins.op_str}")

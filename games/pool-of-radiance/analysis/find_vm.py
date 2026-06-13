import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ov=open(GAME+r"\GAME.OVR","rb").read()
md=Cs(CS_ARCH_X86,CS_MODE_16)
# indirect jump-through-table patterns (16-bit)
PATS=[(b"\xff\xa7","jmp [bx+d16]"),(b"\xff\x27","jmp [bx]"),(b"\x2e\xff\xa7","jmp cs:[bx+d16]"),
      (b"\xff\xa5","jmp [di+d16]"),(b"\xff\x2f","jmp [bx]"),(b"\xff\xe7","jmp di"),(b"\xff\xe3","jmp bx")]
print("indirect-jump dispatch sites in GAME.OVR:")
sites=[]
for pat,desc in PATS:
    i=ov.find(pat)
    while i!=-1:
        sites.append((i,desc)); i=ov.find(pat,i+1)
sites.sort()
print(f"  {len(sites)} total")
# For each site, disassemble ~24 bytes before to see if it's a bytecode dispatcher
# (reads a byte, bounds-checks, scales by 2). Show context.
for off,desc in sites[:14]:
    pre=ov[max(0,off-24):off+4]
    print(f"\n @0x{off:05X} ({desc}):")
    base=max(0,off-24)
    for ins in md.disasm(pre,base):
        mark=" <<<" if ins.address>=off else ""
        print(f"    {ins.address:06X}: {ins.mnemonic:6s} {ins.op_str}{mark}")

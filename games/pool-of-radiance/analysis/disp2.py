from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ov=open(GAME+r"\GAME.OVR","rb").read()
md=Cs(CS_ARCH_X86, CS_MODE_16)
for ins in md.disasm(ov[0x3D4F:0x3DC0], 0x3D4F):
    if ins.mnemonic in ("cmp","jne","je","call","jmp"):
        print(f"  {ins.address:06X}: {ins.mnemonic} {ins.op_str}")

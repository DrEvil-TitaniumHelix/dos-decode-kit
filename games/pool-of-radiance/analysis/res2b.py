from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ex=open(GAME+r"\START.EXE","rb").read()
md=Cs(CS_ARCH_X86,CS_MODE_16)
def foff(seg,off): return 0x200+seg*16+off
def show(seg,off,label,n=40):
    fo=foff(seg,off)
    print(f"\n=== {label}: {seg:04X}:{off:04X} -> file 0x{fo:05X} (len {len(ex)}) ===")
    if fo>=len(ex): print("  OUT OF RANGE"); return
    cnt=0
    for ins in md.disasm(ex[fo:fo+120],fo):
        print(f"  {ins.address:06X}: {ins.mnemonic:7s} {ins.op_str}")
        cnt+=1
        if cnt>=n: break
        if ins.mnemonic in('ret','retf'): break
for off,lbl in [(0x25,"helper25 (get-next-byte operand)"),(0x2a,"helper2a"),
                (0x4d,"helper4d"),(0x52,"helper52"),(0x8e,"helper8e")]:
    show(0x2b,off,lbl)

from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ex=open(GAME+r"\START.EXE","rb").read()
md=Cs(CS_ARCH_X86,CS_MODE_16)
def foff(seg,off): return 0x200+seg*16+off
def show(seg,off,label,n=22):
    fo=foff(seg,off)
    print(f"\n=== {label}: {seg:04X}:{off:04X} -> START.EXE file 0x{fo:05X} ===")
    if fo>=len(ex): print("  out of range"); return
    cnt=0
    for ins in md.disasm(ex[fo:fo+80],fo):
        print(f"  {ins.address:06X}: {' '.join(f'{b:02X}' for b in ins.bytes):<16} {ins.mnemonic:7s} {ins.op_str}")
        cnt+=1
        if cnt>=n: break
# the hot resident helpers seen in GAME.OVR far-calls
show(0xAF8,0xB25,"40-byte copy primitive (from menu-setup fn)")
show(0xAF8,0xB0B,"hot UI routine (very common)")
show(0xAF8,0xDC0,"called by workhorse 0x2B04A")

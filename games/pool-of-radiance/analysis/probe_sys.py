from capstone import *
START=r".\games\pool-of-radiance\extracted\poolrad\START.EXE"
data=open(START,'rb').read()
md=Cs(CS_ARCH_X86,CS_MODE_16)
# SYSTEM seg 0xaf8 FP/runtime routines used by op08: 0x11c0, 0x119a, 0x119e
for seg,off,name in [(0xaf8,0x11c0,"op08 a"),(0xaf8,0x119a,"op08 b"),(0xaf8,0x119e,"op08 c"),(0x709,0xb66,"op0F blit"),(0x709,0x9e3,"op10")]:
    fo=0x200+seg*16+off
    print("="*40,name,"0x%X:0x%X fo=0x%X"%(seg,off,fo))
    cnt=0
    for ins in md.disasm(data[fo:fo+50],off):
        print("  0x%04X: %-9s %s"%(ins.address,ins.mnemonic,ins.op_str))
        cnt+=1
        if ins.mnemonic in('ret','retf') or cnt>=10: break

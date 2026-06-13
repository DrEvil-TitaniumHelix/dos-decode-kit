from capstone import *
# resident seg 0x2b -> START.EXE file offset = 0x200 + seg*16 + off
START = r".\games\pool-of-radiance\extracted\poolrad\START.EXE"
import os
if not os.path.exists(START):
    # try locating START.EXE
    import glob
    cand = glob.glob(r".\games\pool-of-radiance\extracted\poolrad\*.EXE")
    print("EXE candidates:", cand)
else:
    data=open(START,'rb').read()
    print("START.EXE size", len(data))
    md=Cs(CS_ARCH_X86,CS_MODE_16); md.detail=False
    seg=0x2b
    for off in (0x25,0x2a,0x4d,0x52,0x39,0x43,0x48,0x3e,0x5c):
        fo=0x200+seg*16+off
        print("="*50)
        print("helper 0x2b:%04X  fileoff=0x%X"%(off,fo))
        cnt=0
        for ins in md.disasm(data[fo:fo+120], off):
            print("  0x%04X: %-10s %s"%(ins.address,ins.mnemonic,ins.op_str))
            cnt+=1
            if ins.mnemonic in('ret','retf') or cnt>=40: break

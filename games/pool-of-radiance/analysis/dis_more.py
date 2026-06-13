from capstone import *
OVR=r".\games\pool-of-radiance\extracted\poolrad\GAME.OVR"
data=open(OVR,'rb').read()
md=Cs(CS_ARCH_X86,CS_MODE_16)
def dis(a,n=70):
    print("="*60); print("@0x%04X"%a)
    cnt=0
    for ins in md.disasm(data[a:a+500],a):
        print("  0x%04X: %-9s %s"%(ins.address,ins.mnemonic,ins.op_str))
        cnt+=1
        if ins.mnemonic in('ret','retf') or cnt>=n: break
# rest of 0x0E (combat/encounter region) from 0x1667
dis(0x1667,55)

from capstone import *
OVR=r".\games\pool-of-radiance\extracted\poolrad\GAME.OVR"
data=open(OVR,'rb').read()
md=Cs(CS_ARCH_X86,CS_MODE_16)
a=0x126A
cnt=0
for ins in md.disasm(data[a:a+760],a):
    print("  0x%04X: %-9s %s"%(ins.address,ins.mnemonic,ins.op_str))
    cnt+=1
    if cnt>=110: break

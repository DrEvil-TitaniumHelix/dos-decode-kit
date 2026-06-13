from capstone import *
START=r".\games\pool-of-radiance\extracted\poolrad\START.EXE"
data=open(START,'rb').read()
md=Cs(CS_ARCH_X86,CS_MODE_16)
calls={
 "0x709:0xb66 (op0F getstr?)":(0x709,0xb66),
 "0x709:0x9e3 (op10)":(0x709,0x9e3),
 "0x709:0x768 (gethelper?)":(0x709,0x768),
 "0xba:0x767 (op0A move)":(0xba,0x767),
 "0xba:0x48 (rng)":(0xb0,0x48),
 "0x3d0:0x2a (op0E)":(0x3d0,0x2a),
 "0x3d0:0x25 (op0E)":(0x3d0,0x25),
 "0x3ca:0x25 (op0E end)":(0x3ca,0x25),
 "0x3f1:0x2e8 (op0E)":(0x3f1,0x2e8),
 "0x78:0x2a (op0A)":(0x78,0x2a),
}
for name,(seg,off) in calls.items():
    fo=0x200+seg*16+off
    print("="*50); print(name," fileoff=0x%X"%fo)
    if fo+16>len(data):
        print("  OUT OF RANGE (len=0x%X)"%len(data)); continue
    cnt=0
    for ins in md.disasm(data[fo:fo+40],off):
        print("  0x%04X: %-9s %s ; %s"%(ins.address,ins.mnemonic,ins.op_str,data[fo+(ins.address-off):fo+(ins.address-off)+ins.size].hex()))
        cnt+=1
        if cnt>=6: break

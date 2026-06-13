import json
from capstone import *
SEG=r".\games\pool-of-radiance\analysis\overlay_segmap.json"
segmap=json.load(open(SEG))
OVR=r".\games\pool-of-radiance\extracted\poolrad\GAME.OVR"
data=open(OVR,'rb').read()
md=Cs(CS_ARCH_X86,CS_MODE_16)
# The ECL interpreter handlers (0xD47..0x3BC3) are all in one unit. Find which segmap entry covers ovr_off range containing e.g. 0x0F7A.
# Need mapping code-addr -> file offset. The handler addresses given ARE file offsets? Check: handler @0x0F7A disassembled cleanly from data[0x0F7A]. Yes - code addr == file offset for this unit (unit loaded at file region directly). 
# So 0x2b:0x25 unit0 off 0x1CC3 -> file offset? The unit0 base: handlers start ~0xD47, addresses == file offsets, so off 0x1CC3 = file 0x1CC3.
for name,off in [("get_byte_0x25",0x1CC3),("begin_0x2a",0x1DF0),("0x2f",0x1EA6),("0x34",0x1FB1),("readstr_0x39",0x20CC),("store_0x57",0x127A),("0x5c",0x087A)]:
    print("="*55)
    print(name,"@0x%04X"%off)
    cnt=0
    for ins in md.disasm(data[off:off+150],off):
        print("  0x%04X: %-9s %s"%(ins.address,ins.mnemonic,ins.op_str))
        cnt+=1
        if ins.mnemonic in('ret','retf') or cnt>=45: break

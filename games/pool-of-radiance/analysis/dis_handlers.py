import sys
from capstone import *

OVR = r".\games\pool-of-radiance\extracted\poolrad\GAME.OVR"
data = open(OVR,'rb').read()
md = Cs(CS_ARCH_X86, CS_MODE_16)
md.detail = True

# handlers from locate phase (file offsets within GAME.OVR, code addresses)
handlers = {
 0x08:0x0F7A, 0x09:0x0FD8, 0x0A:0x1026, 0x0B:0x1196, 0x0C:0x10FA,
 0x0D:0x155D, 0x0E:0x159C, 0x0F:0x1697,
 # neighbors for context
 0x07:0x0EE9, 0x10:0x16DA,
}

def dis(addr, n=80):
    out=[]
    off=addr
    cnt=0
    for ins in md.disasm(data[off:off+400], addr):
        out.append((ins.address, ins.mnemonic, ins.op_str, data[ins.address:ins.address+ins.size].hex()))
        cnt+=1
        if cnt>=n: break
        # stop at ret
        if ins.mnemonic in ('ret','retf'):
            break
    return out

for op in sorted(handlers):
    a=handlers[op]
    print("="*70)
    print("OPCODE 0x%02X (%d)  handler @0x%04X"%(op,op,a))
    for addr,m,o,hx in dis(a):
        print("  0x%04X: %-22s %-22s ; %s"%(addr,m,o,hx))

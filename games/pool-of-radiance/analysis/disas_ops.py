import sys, json
from capstone import *

OVR = r".\games\pool-of-radiance\extracted\poolrad\GAME.OVR"
data = open(OVR,'rb').read()
md = Cs(CS_ARCH_X86, CS_MODE_16)
md.detail = True

handlers = {
 0x20:0x1917, 0x21:0x19BA, 0x22:0x236F, 0x23:0x240F,
 0x24:0x24E1, 0x25:0x263E, 0x26:0x263E, 0x27:0x26F6,
}

# resident far-call resolver: file = 0x200 + seg*16 + off  (START.EXE) -- but those are START.EXE offsets,
# not GAME.OVR. We just label them. Known game helper segs: 0xBA,0xB0,0x709,0x2B,0xAF8(SYSTEM ignore)
def label_far(seg,off):
    s=f"{seg:#06x}:{off:#06x}"
    tags={0xAF8:"SYSTEM(ignore)",0xBA:"helperBA",0xB0:"helperB0",0x709:"helper709",0x2B:"ECLstream"}
    if seg in tags: s+=f"[{tags[seg]}]"
    return s

def disas(start, n=120, stop_at_ret=True):
    out=[]
    off=start
    count=0
    while count<n and off < len(data):
        chunk=data[off:off+16]
        ins=next(md.disasm(chunk, off),None)
        if ins is None:
            out.append(f"{off:#07x}: db {data[off]:02x}")
            off+=1; count+=1; continue
        txt=f"{ins.address:#07x}: {ins.mnemonic} {ins.op_str}"
        # annotate far calls (9A) lcall ptr16:16
        b=data[ins.address:ins.address+ins.size]
        if b[0]==0x9A and ins.size==5:
            o=b[1]|(b[2]<<8); s=b[3]|(b[4]<<8)
            txt+=f"   ; FAR {label_far(s,o)}"
        out.append(txt)
        off+=ins.size; count+=1
        if stop_at_ret and ins.mnemonic in ('ret','retf') and count>3:
            break
    return "\n".join(out)

target = int(sys.argv[1],16) if len(sys.argv)>1 else None
n = int(sys.argv[2]) if len(sys.argv)>2 else 120
if target is not None:
    print(disas(target,n,stop_at_ret=False))

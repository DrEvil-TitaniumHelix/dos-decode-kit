import json
from capstone import *
seg_off = {
 0x25:0x1CC3, 0x2a:0x1DF0, 0x39:0x20CC,
 # parse remaining from raw dump
}
# From raw: 0x39->CD3F CC 20 00 -> 0x20CC unit00
# 0x3e: bytes "00 00 00 cd 3f 00 00 07" => the CD3F at 0x3e+3? messy. Let's re-scan precisely.
START = r".\games\pool-of-radiance\extracted\poolrad\START.EXE"
data=open(START,'rb').read()
seg=0x2b
base=0x200+seg*16
# Each public entry is 5 bytes: CD 3F + WORD off + BYTE unit. Table is contiguous.
# Walk from off 0x25.. printing 5-byte records
print("addr  bytes            -> int3f? off  unit")
o=0x25
while o<0x70:
    fo=base+o
    b=data[fo:fo+5]
    if b[0]==0xCD and b[1]==0x3F:
        off=b[2]|(b[3]<<8); unit=b[4]
        print("0x%02X: %s -> off=0x%04X unit=0x%02X"%(o,b.hex(' '),off,unit))
        o+=5
    else:
        print("0x%02X: %s (not thunk)"%(o,b.hex(' ')))
        o+=1

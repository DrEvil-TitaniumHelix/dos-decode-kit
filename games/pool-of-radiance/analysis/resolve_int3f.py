START = r".\games\pool-of-radiance\extracted\poolrad\START.EXE"
import struct,json
data=open(START,'rb').read()
# int 3f thunk format (TP overlay): CD 3F <word ovr_seg> <word entry_off>  OR  CD 3F + 3 bytes
# Actually TP: CD 3F  dw <overlay_segment_in_table>  dw <offset>
# Let's just dump raw bytes around each 0x2b:off
seg=0x2b
def dump(off,n=8):
    fo=0x200+seg*16+off
    return data[fo:fo+n].hex(' ')
for off in (0x25,0x2a,0x39,0x3e,0x43,0x48,0x4d,0x52,0x5c):
    print("0x2b:%04X ->"%off, dump(off,8))

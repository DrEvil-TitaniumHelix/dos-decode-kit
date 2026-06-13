GAME=r".\games\pool-of-radiance\extracted\poolrad"
ex=open(GAME+r"\START.EXE","rb").read()
def foff(seg,off): return 0x200+seg*16+off
# FBOV overlay stub: CD 3F <ovr_blocknum word> <entry offset word> typically
import struct
for off in [0x25,0x2a,0x4d,0x52,0x8e]:
    fo=foff(0x2b,off)
    raw=ex[fo:fo+8]
    print(f"2b:{off:02X} @file 0x{fo:05X}: "+' '.join(f'{b:02X}' for b in raw))
    if raw[0:2]==b'\xCD\x3F':
        a,b=struct.unpack('<HH',raw[2:6])
        print(f"    int3F vec: word1=0x{a:04X} word2=0x{b:04X}")

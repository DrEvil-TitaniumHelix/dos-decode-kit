from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ex=open(GAME+r"\START.EXE","rb").read()
import struct
# MZ header
e_cblp,e_cp = struct.unpack('<HH',ex[2:6])
e_cparhdr=struct.unpack('<H',ex[8:10])[0]
hdrlen=e_cparhdr*16
print(f"MZ hdr len=0x{hdrlen:X}, image starts at file 0x{hdrlen:X}")
# The 0x2b segment thunks are CD 3F <ovr_id> <off> per FBOV. Dump the thunk bytes raw for the helpers.
def foff_load(seg,off): return 0x200+seg*16+off  # per locate-phase resident convention
for off in [0x25,0x2a,0x4d,0x52,0x8e]:
    fo=foff_load(0x2b,off)
    print(f"2b:{off:02X} file0x{fo:05X}: "+' '.join(f'{b:02X}' for b in ex[fo:fo+5]))
print()
# The locate phase said resident far-call file = 0x200 + seg*16 + off. But 0x2b thunks
# are int3F stubs. Let's instead find the int3F handler's overlay-table to resolve targets.
# Simpler: dump the whole 0x2b segment region as a thunk array (each 5 bytes: CD 3F id:byte off:word? )
base=foff_load(0x2b,0)
print("0x2b segment thunk dump (file 0x%05X):"%base)
for i in range(0,0xA0,5):
    raw=ex[base+i:base+i+5]
    if raw[0]==0xCD and raw[1]==0x3F:
        idb=raw[2]; offw=struct.unpack('<H',raw[3:5])[0]
        print(f"  off 0x{i:02X}: CD3F id=0x{idb:02X} off=0x{offw:04X}")
    else:
        print(f"  off 0x{i:02X}: "+' '.join(f'{b:02X}' for b in raw)+" (not a stub)")

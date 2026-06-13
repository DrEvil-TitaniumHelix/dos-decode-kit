import struct
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ex=open(GAME+r"\START.EXE","rb").read()
print(f"START.EXE {len(ex)} bytes; header 0x200; load module = {len(ex)-0x200} bytes")
print(f"MZ: e_crlc(relocs)={struct.unpack_from('<H',ex,6)[0]}, entry CS:IP={struct.unpack_from('<H',ex,0x16)[0]:04X}:{struct.unpack_from('<H',ex,0x14)[0]:04X}, e_ss={struct.unpack_from('<H',ex,0x0E)[0]:04X}")

# Find INT 3Fh (CD 3F) occurrences — TP overlay-manager stubs
hits=[]
i=ex.find(b"\xCD\x3F")
while i!=-1:
    hits.append(i); i=ex.find(b"\xCD\x3F",i+1)
print(f"\nINT 3Fh sites: {len(hits)}")
# Stubs sit at paragraph-aligned segment starts. Group by (addr-0x200)//16 alignment
para_aligned=[h for h in hits if (h-0x200)%16==0]
print(f"paragraph-aligned (segment-start) INT 3F: {len(para_aligned)}")
for h in para_aligned[:12]:
    seg=(h-0x200)//16
    after=ex[h:h+32]
    print(f"  file 0x{h:05X} seg 0x{seg:04X}: "+" ".join(f"{x:02X}" for x in after))

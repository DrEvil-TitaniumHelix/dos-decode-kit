import os, sys, re
sys.path.insert(0, r".\kit")
import dax
GAME=r".\games\pool-of-radiance\extracted\poolrad"
d=dax.read_dax(os.path.join(GAME,"ECL1.DAX"))[0]["data"]
def words(buf):
    return len(re.findall(rb"[A-Za-z]{4,}", buf))
print("raw printable words:", words(d))
# try mask 0x7F (strip high bit)
m=bytes(x&0x7F for x in d); print("mask0x7F words:", words(m))
# try XOR keys
for k in [0x80,0x20,0xFF,0x40,0x7F]:
    x=bytes(b^k for b in d); print(f"xor {k:02X} words:", words(x))
# Gold Box: text often stored with +0x?? offset or as 0x80-flagged. Check byte histogram of high range
hi=sum(1 for b in d if b>=0x80); print(f"bytes>=0x80: {hi}/{len(d)} = {100*hi/len(d):.0f}%")
# sample the mask0x7F result around a dense alpha region
ms=re.findall(rb"[\x20-\x7e]{8,}", m)
print("mask0x7F sample strings:", [s.decode()[:40] for s in ms[:8]])

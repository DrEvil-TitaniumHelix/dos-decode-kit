import os, sys, struct
sys.path.insert(0, r".\kit")
import dax
GAME=r".\games\pool-of-radiance\extracted\poolrad"
d=dax.read_dax(os.path.join(GAME,"ECL1.DAX"))[0]["data"]
print(f"ECL1 block18 len={len(d)}")
print("first 64 bytes:")
for off in range(0,64,16): print(f"  {off:03d}: "+" ".join(f"{x:02X}" for x in d[off:off+16]))
# The leading XX YY 01 01 pattern: parse as 4-byte records {u16 val, u16 tag=0x0101}
print("\nleading 4-byte records (while tag==0x0101):")
i=0; recs=[]
while i+4<=len(d):
    val,tag=struct.unpack_from("<HH",d,i)
    if tag!=0x0101: break
    recs.append(val); i+=4
print(f"  {len(recs)} records, then bytecode starts at offset {i}")
print(f"  record values (hex): {[f'{v:04X}' for v in recs[:20]]}")
print(f"  as possible offsets into block (max={max(recs) if recs else 0:04X}, blocklen={len(d):04X})")
# bytecode region opcode frequency (first byte of each... unknown instr len; just byte histogram)
from collections import Counter
bc=d[i:]
print(f"\nbytecode region: {len(bc)} bytes; top byte values:")
c=Counter(bc)
for b,n in c.most_common(16): print(f"   0x{b:02X}: {n}")

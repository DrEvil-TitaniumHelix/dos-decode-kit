import sys
sys.path.insert(0,r'.\kit')
import dax, glob, os
base=r".\games\pool-of-radiance\extracted\poolrad"
# count leading-byte histogram across all ECL bytecode (after 20-byte header)
from collections import Counter
c=Counter()
nblk=0
for p in sorted(glob.glob(base+r"\ECL*.DAX")):
    try: blocks=dax.read_dax(p)
    except Exception as e:
        continue
    for b in blocks:
        d=b["data"]; nblk+=1
        # crude: count all byte values in bytecode region
        for x in d[20:]:
            c[x]+=1
print("blocks:",nblk)
print("byte freq for opcodes 0x08-0x18:")
for op in range(0x08,0x19):
    print(f"  0x{op:02X}: {c.get(op,0)}")

import sys
sys.path.insert(0, 'kit')
import dax, struct
from collections import Counter, defaultdict

base = 'games/pool-of-radiance/extracted/poolrad/'
allblocks = []
for n in range(1, 9):
    for b in dax.read_dax(base + f'ECL{n}.DAX'):
        allblocks.append((n, b['id'], b['data']))

# Greedy decode with tag {0x01:2}. Opcode = any non-0x01 byte; operands = following 01-W tokens.
def decode(bc, start, end):
    out=[]; p=start
    while p<end:
        op=bc[p]; q=p+1; args=[]
        while q+2<end and bc[q]==0x01:
            args.append(bc[q+1]|(bc[q+2]<<8)); q+=3
        out.append((p,op,args)); p=q
    return out

opc=Counter()
arity=defaultdict(Counter)
for n,bid,d in allblocks:
    bc=d[20:]
    for p,op,args in decode(bc,0,len(bc)):
        opc[op]+=1
        arity[op][len(args)]+=1

print(f"distinct leading (opcode) bytes: {len(opc)}")
print("top opcodes by frequency (op: count  arities):")
for op,ct in opc.most_common(50):
    ar=dict(arity[op])
    print(f"  0x{op:02X}: {ct:5d}  arities={ar}")

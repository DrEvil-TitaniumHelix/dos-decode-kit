import sys
sys.path.insert(0, 'kit')
import dax, struct
from collections import Counter, defaultdict

base = 'games/pool-of-radiance/extracted/poolrad/'
allblocks = []
for n in range(1, 9):
    for b in dax.read_dax(base + f'ECL{n}.DAX'):
        allblocks.append((n, b['id'], b['data']))

# BEST MODEL: tagged-operand. opcode = leading byte. operand token 0x01 -> WORD.
# Measure: from EACH handler offset (a known instruction start), decode FORWARD and check
# that decoding from byteoff 0 reaches that same offset (i.e. offset is on a boundary).
def decode_bounds(bc,start,end):
    p=start;bounds=set()
    while p<end:
        bounds.add(p)
        q=p+1
        while q+2<end and bc[q]==0x01:
            q+=3
        p=q
    bounds.add(end)
    return bounds

def targets(d):
    bc=d[20:];L=len(bc);out=[]
    for i in range(1,5):
        v=struct.unpack_from('<H',d,i*4)[0]
        bo=(v&0x7FFF)-5000
        out.append(((v&0x7FFF),bo))
    return out,L

hit=miss=0; miss_ctx=[]
for n,bid,d in allblocks:
    bc=d[20:];tgs,L=targets(d)
    b=decode_bounds(bc,0,L)
    for addr,bo in tgs:
        if not (0<=bo<L): continue
        if bo in b: hit+=1
        else:
            miss+=1
            miss_ctx.append((n,bid,bo,' '.join(f'{x:02X}' for x in bc[bo:bo+10])))
print(f"BEST MODEL (opcode + 0x01-WORD operand): handler-offset boundary hits {hit}, misses {miss}")
print("\nmiss contexts (handlers landing off-boundary; check if they are data tables):")
for n,bid,bo,ctx in miss_ctx:
    print(f"  ECL{n} id{bid} @{bo}: {ctx}")

# Opcode count under this model: leading bytes, but recovered ONLY within in-range code from
# handler-aligned decoding. Count opcode histogram across full decode of every block.
opc=Counter()
for n,bid,d in allblocks:
    bc=d[20:];L=len(bc);p=0
    while p<L:
        opc[bc[p]]+=1
        q=p+1
        while q+2<L and bc[q]==0x01: q+=3
        p=q
under40=sum(c for o,c in opc.items() if o<0x40)
total=sum(opc.values())
print(f"\nopcode instances total={total}; with leading byte <0x40: {under40} ({100*under40/total:.1f}%)")
print(f"distinct leading bytes <0x40: {len([o for o in opc if o<0x40])}")

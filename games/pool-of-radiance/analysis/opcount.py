import sys
sys.path.insert(0, 'kit')
import dax, struct
from collections import Counter

base = 'games/pool-of-radiance/extracted/poolrad/'
allblocks = []
for n in range(1, 9):
    for b in dax.read_dax(base + f'ECL{n}.DAX'):
        allblocks.append((n, b['id'], b['data']))

# Decode every block with {01:2}, count leading opcode bytes ONLY for instructions reachable
# from handler offsets (better signal than raw byte0 of every position).
def walk(bc,start,end,opc):
    p=start
    while p<end:
        opc[bc[p]]+=1
        q=p+1
        while q+2<end and bc[q]==0x01: q+=3
        p=q

opc=Counter()
for n,bid,d in allblocks:
    bc=d[20:]
    walk(bc,0,len(bc),opc)

tot=sum(opc.values())
cum=0;n40=0
print("opcode | count | cum%")
for op,ct in opc.most_common():
    cum+=ct
    if op<0x40: n40+=1
    if cum/tot < 0.985:
        print(f"  0x{op:02X}: {ct:6d}  {100*cum/tot:5.1f}%")
print(f"... distinct leading bytes total={len(opc)}; with value<0x40={n40}")
# how many opcodes cover 95% of instructions?
cum=0;n=0
for op,ct in opc.most_common():
    cum+=ct;n+=1
    if cum/tot>=0.95:
        print(f"top {n} opcodes cover 95% of instruction stream");break
cum=0;n=0
for op,ct in opc.most_common():
    cum+=ct;n+=1
    if cum/tot>=0.99:
        print(f"top {n} opcodes cover 99%");break

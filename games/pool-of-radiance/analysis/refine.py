import sys
sys.path.insert(0, 'kit')
import dax, struct
from collections import Counter

base = 'games/pool-of-radiance/extracted/poolrad/'
allblocks = []
for n in range(1, 9):
    for b in dax.read_dax(base + f'ECL{n}.DAX'):
        allblocks.append((n, b['id'], b['data']))

# Refined operand grammar guess. From miss contexts, the recurring operand encodings are:
#   01 <WORD>      var/address operand  (len 3)
#   00 <BYTE>      small const byte?     (len 2)   e.g. "00 40", "00 02", "00 00", "00 FF"
#   09 <WORD>      const word?           seen "09 00 0B", "09 00 00" => 09 then WORD
#   03 <WORD>      seen "03 01 .." -> 03 then 01-tag => 03 is opcode w/ 01-operand
# Hmm "00 40" appears as operand. Let me treat operand-tags = {0x00:+1, 0x01:+2} only and let
# opcodes be everything else, then re-measure boundaries.
def bounds(bc,end,tags):
    p=0;s=set()
    while p<end:
        s.add(p);q=p+1
        while q<end and bc[q] in tags:
            pl=tags[bc[q]]
            if q+1+pl>end:break
            q+=1+pl
        p=q
    s.add(end);return s

def targets(d):
    bc=d[20:];L=len(bc);out=[]
    for i in range(1,5):
        v=struct.unpack_from('<H',d,i*4)[0]
        out.append((v&0x7FFF)-5000)
    return out,L

for name,tags in [("{01:2}",{0x01:2}),("{00:1,01:2}",{0x00:1,0x01:2}),
                  ("{01:2,09:2}",{0x01:2,0x09:2}),("{00:1,01:2,09:2}",{0x00:1,0x01:2,0x09:2})]:
    hit=tgt=0
    for n,bid,d in allblocks:
        bc=d[20:];tgs,L=targets(d)
        b=bounds(bc,L,tags)
        for t in tgs:
            if 0<=t<L:
                tgt+=1;hit+=(t in b)
    print(f"{name}: {hit}/{tgt}")

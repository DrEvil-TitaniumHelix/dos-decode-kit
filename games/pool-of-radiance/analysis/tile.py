import sys
sys.path.insert(0, 'kit')
import dax, struct
from collections import Counter, defaultdict

base = 'games/pool-of-radiance/extracted/poolrad/'
allblocks = []
for n in range(1, 9):
    for b in dax.read_dax(base + f'ECL{n}.DAX'):
        allblocks.append((n, b['id'], b['data']))

# TAGGED OPERAND reader. Determine tag lengths empirically.
# Known: tag 0x01 -> WORD (2 byte payload).
# Hypothesize the operand grammar used by Gold Box "GetinpArg":
#   tag byte t:
#     0x01 : +2 (WORD constant/var)
#     0x03 : +2 (WORD)   ? we saw "03 01 .." meaning 03 is OPCODE not tag. So don't treat 03 as tag.
# Let's discover tags: an operand-tag should ALWAYS be followed by a consistent payload length.
# Test candidate tag set T={0x00:1,0x01:2}. Operand len = 1+payload.
# Then define instruction by SCANNING: opcode = first byte; then read args greedily while the
# next byte is a known tag; stop when next byte is NOT a tag (=> it's the next opcode).
# This makes opcodes = "non-tag bytes". Measure tiling cleanliness + boundary hits.

def make_decoder(tags):
    def decode(bc, start, end):
        # returns list of (pos, opcode, [args]) ; tiles [start,end)
        out=[]
        p=start
        while p < end:
            op=bc[p]; q=p+1; args=[]
            # read tagged args
            while q < end and bc[q] in tags:
                t=bc[q]; pl=tags[t]
                if q+1+pl>end: break
                val=int.from_bytes(bc[q+1:q+1+pl],'little')
                args.append((t,val)); q+=1+pl
            out.append((p,op,args)); p=q
        return out
    return decode

def targets(d):
    bc=d[20:]; L=len(bc); out=[]
    for i in range(1,5):
        v=struct.unpack_from('<H',d,i*4)[0]
        bo=(v&0x7FFF)-5000
        if 0<=bo<L: out.append(bo)
    return out,L

for tagset_name,tags in [("{01:2}",{0x01:2}),("{00:1,01:2}",{0x00:1,0x01:2}),
                          ("{01:2,03:2,09:2}",{0x01:2,0x03:2,0x09:2})]:
    dec=make_decoder(tags)
    total_hit=0; total_tgt=0; clean=0; tot=0
    for n,bid,d in allblocks:
        bc=d[20:]; tgs,L=targets(d)
        ins=dec(bc,0,L)
        bounds=set(p for p,_,_ in ins)
        bounds.add(L)
        for t in tgs:
            total_tgt+=1
            if t in bounds: total_hit+=1
        tot+=1
    print(f"tagset {tagset_name}: handler-boundary hits {total_hit}/{total_tgt}")

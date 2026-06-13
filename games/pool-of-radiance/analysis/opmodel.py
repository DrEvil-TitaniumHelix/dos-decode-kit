import sys
sys.path.insert(0, 'kit')
import dax, struct
from collections import Counter, defaultdict

base = 'games/pool-of-radiance/extracted/poolrad/'
allblocks = []
for n in range(1, 9):
    for b in dax.read_dax(base + f'ECL{n}.DAX'):
        allblocks.append((n, b['id'], b['data']))

# New model: an ARGUMENT (operand) is self-describing. Look at the first byte of args.
# We confirmed "01 <WORD>" is a var-ref operand. Let me hypothesize the full operand grammar:
#   first byte 'a':
#     a == 0x01 -> next 2 bytes = WORD address/var          (len 3)
#     a == 0x00 -> ??? maybe 0x00 then... we saw "09 00 02 01 .."
#     high bit set (a & 0x80) -> inline small immediate? maybe a&0x7F = value, len 1
# Let's test: an instruction = OPCODE (in 0..0x3F) + fixed args each read by GetArg.
# GetArg(p):
#   t = bc[p]
#   if t == 0x01: return WORD, len 3
#   if t == 0x00: return (next byte), len 2    # "00 02"
#   if t & 0x80:  return t & 0x7f, len 1
#   else: return t (immediate small int 0..0x7f), len 1
# This way EVERY byte that's not an opcode/arg-structural is consumed as an arg.
# But we need to know per-opcode arg counts. Let's first just measure the GetArg token len dist.

def arglen(bc,p,end):
    t=bc[p]
    if t==0x01: return 3
    if t==0x00:
        return 2 if p+1<end else 1
    return 1

# Decode by: opcode then read args until we reach a byte that "looks like" next opcode?
# Instead: brute-force per-opcode arg count by EM:
# Assume opcodes only in 0..0x3f. Decode greedily: opcode=bc[p] (must be <0x40 else treat as
# arg of previous? no). Let's just require opcodes<0x40 and consume following bytes as args
# (each via GetArg) until next byte <0x40 AND not an arg-tag continuation... ambiguous again.
#
# Cleaner: measure, for each leading opcode value v<0x40 at a *known boundary* (handler offset),
# the byte pattern. Already did. Let me instead just trust greedy {01:2} but RESTRICT opcodes:
# treat ONLY bytes <0x40 as opcodes; bytes 0x40..0xFF that aren't part of an 01-token are
# INLINE OPERAND BYTES belonging to the current opcode.
def decode(bc,start,end):
    out=[];p=start
    while p<end:
        op=bc[p];q=p+1;args=[]
        while q<end:
            if bc[q]==0x01 and q+2<end:
                args.append(('W',bc[q+1]|(bc[q+2]<<8)));q+=3
            elif bc[q]>=0x40:
                args.append(('b',bc[q]));q+=1
            else:
                break
        out.append((p,op,args));p=q
    return out

def targets(d):
    bc=d[20:];L=len(bc);out=[]
    for i in range(1,5):
        v=struct.unpack_from('<H',d,i*4)[0]
        bo=(v&0x7FFF)-5000
        if 0<=bo<L: out.append(bo)
    return out,L

opc=Counter();hit=0;tgt=0
for n,bid,d in allblocks:
    bc=d[20:];tgs,L=targets(d)
    ins=decode(bc,0,L)
    bounds=set(p for p,_,_ in ins);bounds.add(L)
    for t in tgs:
        tgt+=1; hit+= (t in bounds)
    for p,op,a in ins: opc[op]+=1
print(f"opcodes<0x40 model: boundary hits {hit}/{tgt}; distinct opcodes={len(opc)}")
print("opcode freq:")
for op,ct in sorted(opc.items()):
    print(f"  0x{op:02X}: {ct}")

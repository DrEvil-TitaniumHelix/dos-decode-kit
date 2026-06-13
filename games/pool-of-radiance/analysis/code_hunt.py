from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ov=open(GAME+r"\GAME.OVR","rb").read()
md=Cs(CS_ARCH_X86, CS_MODE_16)
# Find windows rich in far-call(9A)/far-ret(CB) and standard ops, poor in ASCII.
def score(buf):
    a=sum(1 for x in buf if 0x20<=x<0x7f)/len(buf)   # ascii frac
    fc=buf.count(0x9A)+buf.count(0xCB)+buf.count(0xE8)  # calls/rets
    return a,fc
best=[]
W=256
for off in range(0x200,len(ov)-W,W):
    a,fc=score(ov[off:off+W])
    if a<0.45 and fc>=4: best.append((off,a,fc))
print(f"candidate code windows: {len(best)}")
# disassemble the first few and show; look for call/ret/mov-heavy coherent runs
import itertools
COMMON={'mov','push','pop','call','ret','retf','jmp','je','jne','jz','jnz','add','sub','cmp','test','lea','xor','or','and','inc','dec','les','lds','loop','cld'}
def coherence(buf,base):
    ins=list(md.disasm(buf,base))
    if not ins: return 0,ins
    return sum(1 for i in ins if i.mnemonic in COMMON)/len(ins), ins
shown=0
for off,a,fc in best:
    coh,ins=coherence(ov[off:off+96],off)
    if coh>0.7 and len(ins)>20:
        print(f"\n=== 0x{off:05X} ascii={a:.2f} calls={fc} coherence={coh:.2f} ===")
        for i in ins[:26]:
            print(f"  {i.address:06X}: {i.mnemonic:7s} {i.op_str}")
        shown+=1
    if shown>=3: break

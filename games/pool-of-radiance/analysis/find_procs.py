from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ov=open(GAME+r"\GAME.OVR","rb").read()
md=Cs(CS_ARCH_X86, CS_MODE_16); md.detail=False

# Find Turbo Pascal proc prologues: 55 8B EC (push bp; mov bp,sp)
sig=b"\x55\x8b\xec"
hits=[]
i=ov.find(sig)
while i!=-1:
    hits.append(i); i=ov.find(sig,i+1)
print(f"'push bp;mov bp,sp' prologues: {len(hits)}")
# histogram by 0x2000 bucket to find the code mass
from collections import Counter
buckets=Counter(h//0x2000 for h in hits)
print("density by 0x2000 region (region: count):")
for k in sorted(buckets): print(f"  0x{k*0x2000:05X}: {buckets[k]}")

# also far-return 0xCB count and int 21h (CD 21)
print(f"\nfar 'retf'(CB) bytes: {ov.count(0xCB)}  ;  'int 21h'(CD21): {ov.count(bytes([0xCD,0x21]))}")

# disassemble a real procedure: take the first prologue in the densest region
dense=max(buckets, key=buckets.get)*0x2000
first=next(h for h in hits if h>=dense)
print(f"\n=== procedure @ 0x{first:05X} (densest code region) ===")
cnt=0
for ins in md.disasm(ov[first:first+160], first):
    print(f"  {ins.address:06X}: {ins.mnemonic:7s} {ins.op_str}")
    cnt+=1
    if ins.mnemonic in ('ret','retf') or cnt>=40: break

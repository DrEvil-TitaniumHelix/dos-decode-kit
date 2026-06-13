import sys
sys.path.insert(0,r'.\kit')
import dax, glob, os, collections

ECLDIR=r".\games\pool-of-radiance\extracted\poolrad"
files=sorted(glob.glob(os.path.join(ECLDIR,"ECL*.DAX")))
# gather all bytecode (skip 20-byte header)
allbc=[]
for f in files:
    for e in dax.read_dax(f):
        d=e["data"]
        if len(d)>20:
            allbc.append((os.path.basename(f),e["id"],d))

# count leading-byte freq of full corpus for reference
cnt=collections.Counter()
for _,_,d in allbc:
    for b in d[20:]:
        cnt[b]+=1
print("top bytes:", [(f'{b:02X}',c) for b,c in cnt.most_common(20)])

# show context around each target opcode by scanning; print byte windows where byte==target
for target in range(0x18,0x20):
    hits=0
    samples=[]
    for fn,bid,d in allbc:
        bc=d[20:]
        for i,b in enumerate(bc):
            if b==target:
                hits+=1
                if len(samples)<6:
                    w=bc[max(0,i-1):i+8]
                    samples.append((fn,bid,i,' '.join(f'{x:02X}' for x in w)))
    print(f"\nopcode 0x{target:02X}: {hits} raw-byte occurrences (UNALIGNED, includes operand collisions)")
    for s in samples: print("   ",s)

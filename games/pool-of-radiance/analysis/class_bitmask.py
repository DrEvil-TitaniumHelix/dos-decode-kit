import os
GAME=r".\games\pool-of-radiance\extracted\poolrad"
recs=[open(os.path.join(GAME,f"CHRDATA{n}.SAV"),"rb").read() for n in range(1,7)]
names=['THRENDER(F)','BAKSHI(F)','RHIANNON(F/MU)','SEAN(C)','DARKSTAR(MU)','PHINEAS(T)']
# Expected class bitmask if Cleric=1,Fighter=2,MU=4,Thief=8:
# THRENDER=2, BAKSHI=2, RHIANNON=6(F+MU), SEAN=1, DARK=4, PHIN=8
# But try ALL bit assignments. A valid class field must satisfy:
#  - THRENDER==BAKSHI (both single-class Fighter)
#  - RHIANNON = THRENDER | (one of SEAN/DARK/PHIN's bit)  (multiclass = OR of single bits)
#  - SEAN, DARK, PHIN are 3 distinct single bits, != Fighter bit
def popcount(x): return bin(x).count('1')
print("Scanning for class-bitmask offsets (THRENDER==BAKSHI, RHIANNON=2-bit combo incl Fighter's bit)...")
hits=[]
for off in range(285):
    v=[r[off] for r in recs]
    if v[0]!=v[1] or v[0]==0: continue          # fighters must match, nonzero
    fb=v[0]
    if popcount(fb)!=1: continue                # single-class fighter = 1 bit
    # the three casters/thief should be single distinct bits
    singles=[v[3],v[4],v[5]]
    if not all(popcount(s)==1 for s in singles): continue
    if len(set([fb]+singles))!=4: continue       # 4 distinct single bits
    # RHIANNON should be fighter-bit OR'd with one of the others
    if popcount(v[2])==2 and (v[2]&fb)==fb and (v[2]&~fb) in singles:
        hits.append((off,v))
for off,v in hits:
    print(f"  *** off {off}: "+"  ".join(f"{n}={x}({x:04b})" for n,x in zip(names,v)))
if not hits:
    print("  no perfect bitmask. Showing offsets where THRENDER==BAKSHI and all 6 distinct-ish:")
    for off in range(285):
        v=[r[off] for r in recs]
        if v[0]==v[1] and v[0]!=0 and len(set(v))>=4 and max(v)<16:
            print(f"  off {off}: "+" ".join(f"{x}" for x in v)+f"   ({names})" if off<0 else f"  off {off}: "+" ".join(str(x) for x in v))

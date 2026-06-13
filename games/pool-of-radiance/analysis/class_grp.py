import os
GAME=r".\games\pool-of-radiance\extracted\poolrad"
recs=[open(os.path.join(GAME,f"CHRDATA{n}.SAV"),"rb").read() for n in range(1,7)]
names=['THRENDER','BAKSHI','RHIANNON','SEAN','DARKSTAR','PHINEAS']
known=['F','F','F/MU','C','MU','T']
print("bytes 278..284 across the 6 chars:")
for off in range(278,285):
    v=[r[off] for r in recs]
    print(f"  off {off}: "+"  ".join(f"{n[:4]}={x:3d}" for n,x in zip(names,v)))
print("\nknown classes:", list(zip(names,known)))
# off 284 hypothesis: 9=Fighter-group, 6=Priest, 12=Mage/Thief-group
print("\noff 284 grouping:")
g={}
for n,r in zip(names,recs): g.setdefault(r[284],[]).append(n)
for k,v in sorted(g.items()): print(f"  value {k}: {v}")
# Is there a byte that splits MU(DARKSTAR) from Thief(PHINEAS)? thief skills already do, but look:
print("\nlooking for a byte splitting DARKSTAR vs PHINEAS but grouping the 3 fighters:")
for off in range(285):
    v=[r[off] for r in recs]
    if v[0]==v[1]==v[2] and v[4]!=v[5] and v[0]!=0 and len(set(v))>=3 and max(v)<64:
        print(f"  off {off}: "+"  ".join(f"{n[:4]}={x}" for n,x in zip(names,v)))

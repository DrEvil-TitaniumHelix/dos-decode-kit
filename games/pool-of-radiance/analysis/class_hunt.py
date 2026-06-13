import os
GAME=r".\games\pool-of-radiance\extracted\poolrad"
recs=[(open(os.path.join(GAME,f"CHRDATA{n}.SAV"),"rb").read()) for n in range(1,7)]
names=['THREN(F)','BAKSHI(F)','RHIAN(?)','SEAN(C)','DARK(MU)','PHIN(T)']
# known: F,F,?,C,MU,T. Look for a byte that groups these as distinct classes.
# AD&D class enums (Gold Box): often Cleric=0,Fighter=1,MagicUser=2,Thief=3 or a bitmask.
print("offsets where the value pattern could be CLASS (distinct per class, F==F):")
for off in range(0,285):
    vals=[r[off] for r in recs]
    # THRENDER and BAKSHI are both Fighter -> should match if this is class
    if vals[0]==vals[1] and len(set(vals))>=3 and max(vals)<32:
        print(f"  off {off:3d}: "+"  ".join(f"{n}={v}" for n,v in zip(names,vals)))

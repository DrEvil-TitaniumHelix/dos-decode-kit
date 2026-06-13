import os
GAME=r".\games\pool-of-radiance\extracted\poolrad"
recs=[]
for n in range(1,7):
    b=open(os.path.join(GAME,f"CHRDATA{n}.SAV"),"rb").read()
    recs.append((b[1:1+b[0]].decode('latin1'),b))
names=[r[0] for r in recs]
print("chars:",names)
# show offsets 16..64 and 100..130 as a per-char table (the stat/class region)
def tab(lo,hi):
    print(f"\noff   "+ "  ".join(f"{n[:8]:>8}" for n in names))
    for off in range(lo,hi):
        vals=[r[1][off] if off<len(r[1]) else 0 for r in recs]
        if len(set(vals))>1:  # only varying offsets
            print(f"  {off:3d}: "+"  ".join(f"{v:8d}" for v in vals))
print("=== VARYING bytes, offsets 16-64 (stats/class/race/level) ===")
tab(16,64)
print("\n=== VARYING bytes, offsets 100-130 ===")
tab(100,130)
# ability scores at 16-21 for reference
print("\nabilities@16 (STR INT WIS DEX CON CHA):")
for n,b in recs: print(f"  {n:16s}",list(b[16:22]))

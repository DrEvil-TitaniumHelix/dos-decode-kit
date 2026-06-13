import os
GAME=r".\games\pool-of-radiance\extracted\poolrad"
for n in [1,2,3]:
    p=os.path.join(GAME,f"CHRDATA{n}.SAV")
    b=open(p,"rb").read()
    name=bytes(c for c in b[:20] if 32<=c<127)
    print(f"CHRDATA{n}.SAV ({len(b)}B): first16={' '.join(f'{x:02X}' for x in b[:16])}")
    print(f"   ascii head: {b[:24]!r}")

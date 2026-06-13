import os
GAME=r".\games\pool-of-radiance\extracted\poolrad"
def dump(n):
    b=open(os.path.join(GAME,f"CHRDATA{n}.SAV"),"rb").read()
    print(f"\n=== CHRDATA{n}.SAV ({len(b)} bytes) name={b[1:1+b[0]].decode('latin1')} ===")
    for off in range(0,len(b),16):
        chunk=b[off:off+16]
        print(f"  {off:03X}({off:3d}): "+" ".join(f"{x:02X}" for x in chunk))
dump(1)
# THRENDER GRONE stats at 16: 11 0C 0C 11 10 0F = STR17 INT12 WIS12 DEX17 CON16 CHA15

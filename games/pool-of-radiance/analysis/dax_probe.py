"""DAX archive format probe for Pool of Radiance (1988, SSI Gold Box).

Goal: reverse the .DAX container format from bytes alone, then validate the
hypothesis across all 113 archives. No assumptions from docs — header first.
"""
import os, struct, glob, collections

GAME = r".\games\pool-of-radiance\extracted\poolrad"

def hexdump(b, n=64):
    out = []
    for i in range(0, min(len(b), n), 16):
        chunk = b[i:i+16]
        hexs = " ".join(f"{x:02X}" for x in chunk)
        asci = "".join(chr(x) if 32 <= x < 127 else "." for x in chunk)
        out.append(f"  {i:04X}  {hexs:<48}  {asci}")
    return "\n".join(out)

def probe_one(path):
    with open(path, "rb") as f:
        b = f.read()
    name = os.path.basename(path)
    print(f"\n=== {name}  ({len(b)} bytes) ===")
    print(hexdump(b, 80))

# Look at a spread of types: tiles, bodies, combat pics, etc.
samples = ["8X8D1.DAX", "BODY1.DAX", "CPIC1.DAX", "COMSPR.DAX", "BACPAC.DAX", "CHEAD.DAX"]
for s in samples:
    p = os.path.join(GAME, s)
    if os.path.exists(p):
        probe_one(p)

# Header-word survey across ALL DAX files: first 2 bytes as LE u16 (likely block count)
print("\n\n=== FIRST-WORD SURVEY (all DAX) ===")
firstword = collections.Counter()
allfiles = sorted(glob.glob(os.path.join(GAME, "*.DAX")))
for p in allfiles:
    with open(p, "rb") as f:
        head = f.read(16)
    w0 = struct.unpack_from("<H", head, 0)[0]
    b0 = head[0]
    firstword[b0] += 1
print(f"{len(allfiles)} DAX files. First-BYTE distribution (likely block count):")
for k in sorted(firstword):
    print(f"  count={k:3d}  ->  {firstword[k]} files")

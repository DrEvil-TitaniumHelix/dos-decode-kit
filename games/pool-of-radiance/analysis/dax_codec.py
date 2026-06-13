"""Reverse the DAX packed-block compression from bytes.

We know each block's exact unpacked size, so any candidate decoder is
VALIDATED iff it consumes exactly packed_size input bytes and emits exactly
unpacked_size output bytes. That's a hard oracle — no plausibility guessing.
"""
import os, struct, glob

GAME = r".\games\pool-of-radiance\extracted\poolrad"

def parse(b):
    hdr = struct.unpack_from("<H", b, 0)[0]
    n = hdr // 9
    entries = []
    pos = 2
    for _ in range(n):
        eid, off, unp, pk = struct.unpack_from("<BIHH", b, pos)
        entries.append(dict(id=eid, off=off, unp=unp, pk=pk))
        pos += 9
    data = b[2 + hdr:]
    for e in entries:
        e["raw"] = data[e["off"]:e["off"] + e["pk"]]
    return entries

def hexdump(b, n=64):
    out = []
    for i in range(0, min(len(b), n), 16):
        chunk = b[i:i+16]
        hexs = " ".join(f"{x:02X}" for x in chunk)
        out.append(f"  {i:04X}  {hexs}")
    return "\n".join(out)

# Look at a few small packed blocks raw.
for fn in ["CHEAD.DAX", "BODY1.DAX"]:
    with open(os.path.join(GAME, fn), "rb") as f:
        b = f.read()
    es = parse(b)
    e = es[0]
    print(f"\n=== {fn} block id={e['id']} packed={e['pk']} unpacked={e['unp']} ratio={e['unp']/e['pk']:.2f} ===")
    print("RAW PACKED:")
    print(hexdump(e["raw"], 64))


# ---- Candidate RLE decoders. Validate by exact length match. ----
def rle_signbyte(src, target):
    """Classic SSI/'Atari' RLE: signed control byte c.
       c >= 0 (0..127): copy c+1 literal bytes.
       c <  0 (0x81..0xFF): repeat next byte (1-c) times  [i.e. 2..128].
       c == 0x80: often a no-op/terminator."""
    out = bytearray()
    i = 0
    while i < len(src) and len(out) < target:
        c = src[i]; i += 1
        if c < 0x80:           # literal run of c+1
            run = c + 1
            out += src[i:i+run]; i += run
        elif c == 0x80:
            break
        else:                  # 0x81..0xFF -> repeat
            cnt = 257 - c      # 0x81->128 ... 0xFF->2
            if i >= len(src): break
            out += bytes([src[i]]) * cnt; i += 1
    return bytes(out), i

def rle_pcx(src, target):
    """PCX-style: if (c & 0xC0)==0xC0 -> repeat next byte (c&0x3F) times, else literal c."""
    out = bytearray(); i = 0
    while i < len(src) and len(out) < target:
        c = src[i]; i += 1
        if (c & 0xC0) == 0xC0:
            cnt = c & 0x3F
            if i >= len(src): break
            out += bytes([src[i]]) * cnt; i += 1
        else:
            out.append(c)
    return bytes(out), i

def rle_hibit_count(src, target):
    """c high-bit = mode. c&0x7f = count n (n>=1).
       hibit set -> repeat next byte n times; clear -> copy n literals."""
    out = bytearray(); i = 0
    while i < len(src) and len(out) < target:
        c = src[i]; i += 1
        n = c & 0x7F
        if n == 0:
            break
        if c & 0x80:
            if i >= len(src): break
            out += bytes([src[i]]) * n; i += 1
        else:
            out += src[i:i+n]; i += n
    return bytes(out), i

decoders = {
    "signbyte": rle_signbyte,
    "pcx": rle_pcx,
    "hibit_count": rle_hibit_count,
}

print("\n\n=== CODEC VALIDATION across all blocks ===")
allfiles = sorted(glob.glob(os.path.join(GAME, "*.DAX")))
results = {k: [0, 0] for k in decoders}  # name -> [exact, total]
for p in allfiles:
    with open(p, "rb") as f:
        b = f.read()
    for e in parse(b):
        for name, fn in decoders.items():
            out, consumed = fn(e["raw"], e["unp"])
            ok = (len(out) == e["unp"])
            results[name][1] += 1
            if ok:
                results[name][0] += 1
for name, (ex, tot) in results.items():
    print(f"  {name:<14}: {ex}/{tot} blocks decode to exact unpacked size")

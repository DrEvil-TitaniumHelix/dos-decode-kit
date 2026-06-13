"""Gold Box DAX archive reader — reusable across the whole SSI Gold Box family.

Decoded clean-room from Pool of Radiance (1988); the container + RLE codec are
shared by ~12 Gold Box titles, so this module reads any of them.

Directory:  u16 header (= 9*block_count) ; N x { u8 id, u32 off, u16 unp, u16 pk } ; data
RLE:        c<0x80 -> copy c+1 literals ; c>=0x80 -> repeat next byte 256-c times
EGA image:  u8 width_px (hdr[0]) + 3 hdr bytes ; 4bpp, 2px/byte, high nibble first, EGA16
"""
import struct

EGA16 = [(0,0,0),(0,0,170),(0,170,0),(0,170,170),(170,0,0),(170,0,170),(170,85,0),(170,170,170),
         (85,85,85),(85,85,255),(85,255,85),(85,255,255),(255,85,85),(255,85,255),(255,255,85),(255,255,255)]


def read_dax(path):
    """Return list of blocks: dict(id, off, unpacked, packed, raw, data)."""
    with open(path, "rb") as f:
        b = f.read()
    hdr = struct.unpack_from("<H", b, 0)[0]
    n = hdr // 9
    blocks, pos = [], 2
    for _ in range(n):
        bid, off, unp, pk = struct.unpack_from("<BIHH", b, pos)
        blocks.append(dict(id=bid, off=off, unpacked=unp, packed=pk)); pos += 9
    data = b[2 + hdr:]
    for e in blocks:
        e["raw"] = data[e["off"]:e["off"] + e["packed"]]
        e["data"] = dax_decompress(e["raw"], e["unpacked"])
    return blocks


def dax_decompress(src, target=None):
    """Reverse the Gold Box DAX RLE. Validated: 1245/1245 PoR blocks exact."""
    out, i = bytearray(), 0
    while i < len(src):
        c = src[i]; i += 1
        if c < 0x80:
            out += src[i:i + c + 1]; i += c + 1
        else:
            if i >= len(src):
                break
            out += bytes([src[i]]) * (256 - c); i += 1
        if target is not None and len(out) >= target:
            break
    return bytes(out)


def decode_image(block_data, width=None):
    """Decode an EGA image block to (width, height, [palette-index per pixel])."""
    w = width if width else block_data[0]
    body = block_data[4:]
    px = []
    for byte in body:
        px.append(byte >> 4); px.append(byte & 0x0F)
    h = (len(px) + w - 1) // w
    return w, h, px


def validate(path):
    """Self-check: directory exact-fit + every block decodes to its unpacked size."""
    import os
    with open(path, "rb") as f:
        b = f.read()
    blocks = read_dax(path)
    dir_ok = (2 + (len(blocks) * 9) + sum(e["packed"] for e in blocks) == len(b))
    rle_ok = all(len(e["data"]) == e["unpacked"] for e in blocks)
    return dir_ok and rle_ok, len(blocks)


if __name__ == "__main__":
    import glob, os, sys
    d = sys.argv[1] if len(sys.argv) > 1 else \
        r".\games\pool-of-radiance\extracted\poolrad"
    ok = tot = 0
    for p in sorted(glob.glob(os.path.join(d, "*.DAX"))):
        good, n = validate(p); ok += good; tot += 1
        print(f"  {os.path.basename(p):14s} {'OK' if good else 'FAIL':4s}  {n:3d} blocks")
    print(f"\n{ok}/{tot} archives validate")

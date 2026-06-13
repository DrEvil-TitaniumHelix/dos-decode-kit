"""DAX extractor + directory dumper for Pool of Radiance.

Directory format (decoded from bytes, offset-chain verified):
  header: 2 bytes (semantics TBD)
  N entries x 9 bytes: { id:u8, offset:u32(LE), unpacked:u16(LE), packed:u16(LE) }
  data section follows; entry.offset is relative to start of data section.

N is recovered by walking entries while the offset-chain stays consistent
(off[k] == off[k-1] + packed[k-1]) and the directory end == data start.
"""
import os, struct, glob

GAME = r".\games\pool-of-radiance\extracted\poolrad"

def parse_dir(b):
    """Return (header_word, entries) where each entry = dict(id,off,unp,pk)."""
    hdr = struct.unpack_from("<H", b, 0)[0]
    # Walk entries; data section starts at 2 + 9*N. block0.off==0, and each
    # subsequent off == running sum of packed sizes. Find N where the directory
    # exactly meets the data section (off[0] maps to file pos 2+9*N).
    entries = []
    pos = 2
    running = 0
    while pos + 9 <= len(b):
        eid, off, unp, pk = struct.unpack_from("<BIHH", b, pos)
        # Heuristic stop: if this "entry" would point past EOF wildly, stop.
        if off != running:
            break
        entries.append(dict(id=eid, off=off, unp=unp, pk=pk))
        running += pk
        pos += 9
        # Does the directory-so-far + data == file size, with this being last?
        data_start = 2 + 9 * len(entries)
        if data_start + running == len(b):
            return hdr, entries, data_start
    # Fallback: best-effort
    data_start = 2 + 9 * len(entries)
    return hdr, entries, data_start

def summarize(path):
    with open(path, "rb") as f:
        b = f.read()
    name = os.path.basename(path)
    hdr, entries, ds = parse_dir(b)
    total_data = sum(e["pk"] for e in entries)
    ok = (ds + total_data == len(b))
    ids = [e["id"] for e in entries]
    return name, len(b), hdr, len(entries), ds, ok, ids

print(f"{'file':<14}{'size':>7}{'hdr':>7}{'N':>4}{'dstart':>8}{'exact?':>8}  ids")
allfiles = sorted(glob.glob(os.path.join(GAME, "*.DAX")))
exact = 0
for p in allfiles:
    name, sz, hdr, n, ds, ok, ids = summarize(p)
    if ok:
        exact += 1
    idstr = ",".join(str(i) for i in ids[:8]) + ("..." if len(ids) > 8 else "")
    print(f"{name:<14}{sz:>7}{hdr:>7}{n:>4}{ds:>8}{str(ok):>8}  {idstr}")
print(f"\nEXACT-FIT directory parse: {exact}/{len(allfiles)} files")

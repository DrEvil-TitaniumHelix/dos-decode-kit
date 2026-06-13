"""Pool of Radiance ECL text codec — 6-bit packed charset.
Decompressor: GAME.OVR 0x8626 (unpacker) + 0x7BA6 (char remap).
Scheme: characters are 6-bit codes packed 4-per-3-bytes MSB-first.
  code 0x00..0x1F  -> ASCII code+0x40  ('@'..'_', i.e. A-Z and a few symbols)
  code 0x20..0x3F  -> ASCII code       (space, ! " ' , . 0-9 : ; etc.)
  code 0x00        -> string terminator
Bit layout per 3-byte group b0 b1 b2:
  c0 = b0>>2
  c1 = ((b0&3)<<4) | (b1>>4)
  c2 = ((b1&0xF)<<2) | (b2>>6)
  c3 = b2&0x3F
(the engine computes this via a rolling 2-byte window + phase 1..4)
"""
def _chmap(c):
    return (c + 0x40) & 0xFF if c <= 0x1f else c

def decode_string(buf, pos, maxchars=255):
    out = []; phase = 1; cur = 0; prev = 0; p = pos; n = 0
    while n < maxchars and p < len(buf):
        if phase < 4:
            prev = cur; cur = buf[p]; p += 1
        if   phase == 1: c = (cur >> 2) & 0x3F
        elif phase == 2: c = (((prev & 3) << 4) | (cur >> 4)) & 0x3F
        elif phase == 3: c = (((prev & 0xF) << 2) | (cur >> 6)) & 0x3F
        else:            c = cur & 0x3F
        phase = phase + 1 if phase < 4 else 1
        if c == 0: break
        out.append(_chmap(c)); n += 1
    return bytes(out), p

def scan_strings(buf, min_len=12):
    """Find all readable strings by trying each alignment; keep maximal English runs."""
    import re
    found = []
    pos = 0
    seen = set()
    while pos < len(buf) - 3:
        s, end = decode_string(buf, pos, 255)
        # require it to look like english: mostly A-Z, space, punctuation, and length
        if len(s) >= min_len:
            letters = sum(1 for b in s if 0x41 <= b <= 0x5a or 0x61 <= b <= 0x7a or b == 0x20)
            if letters / len(s) > 0.88 and re.search(rb'[A-Z]{2,}', s):
                found.append((pos, s.decode('latin1')))
                pos = end
                continue
        pos += 1
    return found

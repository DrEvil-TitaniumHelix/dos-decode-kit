# Generates UI chrome art for the faithful recreation: rope border tiles, gold
# corner ornaments, and a blocky bitmap font. Pure original art design — no game
# files are read. Emits reproduction/ui_art.js (pixel arrays) and a proof PNG.
import os, json
from PIL import Image

OUT = r".\games\pool-of-radiance\reproduction"

# palette indices used in the JS arrays
PAL = ["#000000", "#AA0000", "#FF5555", "#FFFF55", "#AA5500"]
K, R, L, G, B = 0, 1, 2, 3, 4

T = 7          # rope band thickness
TILE_W = 8     # repeat length

def rope_h():
    """Horizontal rope band tile, TILE_W x T. Twisted-cord look: each strand
    crosses the band as a curved lobe (crescent), not a straight stripe."""
    px = [[K] * TILE_W for _ in range(T)]
    # strand cross-section: gap, shadow-red, highlight, red body
    STRIPE = [K, K, R, L, L, R, R, R]
    # horizontal shift per row — bends the strand into a ')' lobe
    CURVE = [3, 1, 0, 0, 0, 1, 3]
    for y in range(T):
        for x in range(TILE_W):
            c = STRIPE[(x + CURVE[y]) % len(STRIPE)]
            # taper: outermost rows lose the highlight (cord rounds away)
            if y in (0, T - 1) and c == L:
                c = R
            px[y][x] = c
    return px

def rope_v():
    h = rope_h()
    # rotate 90 degrees: vertical band T wide, TILE_W tall
    return [[h[x][y] for x in range(T)] for y in range(TILE_W)]

def corner():
    """9x9 gold square ornament with black outline and red center dot."""
    S = 9
    px = [[G] * S for _ in range(S)]
    for i in range(S):
        px[0][i] = px[S - 1][i] = px[i][0] = px[i][S - 1] = K
    # inner shading: bottom/right edge brown for bevel
    for i in range(1, S - 1):
        px[S - 2][i] = B
        px[i][S - 2] = B
    for y in (3, 4, 5):
        for x in (3, 4, 5):
            px[y][x] = R
    return px

# ---- 5x7 font, bolded to 2px strokes (6px wide) ----
FONT57 = {
 'A':[0x0E,0x11,0x11,0x1F,0x11,0x11,0x11], 'B':[0x1E,0x11,0x11,0x1E,0x11,0x11,0x1E],
 'C':[0x0E,0x11,0x10,0x10,0x10,0x11,0x0E], 'D':[0x1E,0x11,0x11,0x11,0x11,0x11,0x1E],
 'E':[0x1F,0x10,0x10,0x1E,0x10,0x10,0x1F], 'F':[0x1F,0x10,0x10,0x1E,0x10,0x10,0x10],
 'G':[0x0E,0x11,0x10,0x17,0x11,0x11,0x0F], 'H':[0x11,0x11,0x11,0x1F,0x11,0x11,0x11],
 'I':[0x0E,0x04,0x04,0x04,0x04,0x04,0x0E], 'J':[0x07,0x02,0x02,0x02,0x02,0x12,0x0C],
 'K':[0x11,0x12,0x14,0x18,0x14,0x12,0x11], 'L':[0x10,0x10,0x10,0x10,0x10,0x10,0x1F],
 'M':[0x11,0x1B,0x15,0x15,0x11,0x11,0x11], 'N':[0x11,0x19,0x15,0x13,0x11,0x11,0x11],
 'O':[0x0E,0x11,0x11,0x11,0x11,0x11,0x0E], 'P':[0x1E,0x11,0x11,0x1E,0x10,0x10,0x10],
 'Q':[0x0E,0x11,0x11,0x11,0x15,0x12,0x0D], 'R':[0x1E,0x11,0x11,0x1E,0x14,0x12,0x11],
 'S':[0x0F,0x10,0x10,0x0E,0x01,0x01,0x1E], 'T':[0x1F,0x04,0x04,0x04,0x04,0x04,0x04],
 'U':[0x11,0x11,0x11,0x11,0x11,0x11,0x0E], 'V':[0x11,0x11,0x11,0x11,0x11,0x0A,0x04],
 'W':[0x11,0x11,0x11,0x15,0x15,0x1B,0x11], 'X':[0x11,0x11,0x0A,0x04,0x0A,0x11,0x11],
 'Y':[0x11,0x11,0x0A,0x04,0x04,0x04,0x04], 'Z':[0x1F,0x01,0x02,0x04,0x08,0x10,0x1F],
 '0':[0x0E,0x11,0x13,0x15,0x19,0x11,0x0E], '1':[0x04,0x0C,0x04,0x04,0x04,0x04,0x0E],
 '2':[0x0E,0x11,0x01,0x06,0x08,0x10,0x1F], '3':[0x0E,0x11,0x01,0x06,0x01,0x11,0x0E],
 '4':[0x02,0x06,0x0A,0x12,0x1F,0x02,0x02], '5':[0x1F,0x10,0x1E,0x01,0x01,0x11,0x0E],
 '6':[0x06,0x08,0x10,0x1E,0x11,0x11,0x0E], '7':[0x1F,0x01,0x02,0x04,0x08,0x08,0x08],
 '8':[0x0E,0x11,0x11,0x0E,0x11,0x11,0x0E], '9':[0x0E,0x11,0x11,0x0F,0x01,0x02,0x0C],
 ' ':[0,0,0,0,0,0,0],
 '.':[0,0,0,0,0,0x0C,0x0C], ',':[0,0,0,0,0x0C,0x04,0x08],
 ':':[0,0x0C,0x0C,0,0x0C,0x0C,0], '-':[0,0,0,0x1E,0,0,0],
 "'":[0x04,0x04,0x08,0,0,0,0], '!':[0x04,0x04,0x04,0x04,0x04,0,0x04],
 '?':[0x0E,0x11,0x01,0x06,0x04,0,0x04], '/':[0x01,0x01,0x02,0x04,0x08,0x10,0x10],
 '(':[0x02,0x04,0x08,0x08,0x08,0x04,0x02], ')':[0x08,0x04,0x02,0x02,0x02,0x04,0x08],
 '&':[0x0C,0x12,0x14,0x08,0x15,0x12,0x0D], '<':[0x02,0x04,0x08,0x10,0x08,0x04,0x02],
 '>':[0x08,0x04,0x02,0x01,0x02,0x04,0x08],
}

def bold(rows):
    return [((r << 1) | r) & 0x3F for r in rows]

FONT = {ch: bold(rows) for ch, rows in FONT57.items()}

# ---- proof sheet ----
def blit(im, px, ox, oy, scale):
    for y, row in enumerate(px):
        for x, c in enumerate(row):
            if c == K:
                continue
            r, g, b = tuple(int(PAL[c][i:i+2], 16) for i in (1, 3, 5))
            for dy in range(scale):
                for dx in range(scale):
                    im.putpixel((ox + x*scale + dx, oy + y*scale + dy), (r, g, b))

def draw_text(im, s, ox, oy, color, scale):
    r, g, b = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    for ci, ch in enumerate(s.upper()):
        rows = FONT.get(ch)
        if not rows:
            continue
        for y, rowbits in enumerate(rows):
            for x in range(6):
                if rowbits & (1 << (5 - x)):
                    for dy in range(scale):
                        for dx in range(scale):
                            im.putpixel((ox + (ci*8 + x)*scale + dx, oy + y*scale + dy), (r, g, b))

def proof():
    S = 4
    im = Image.new("RGB", (340 * S, 120 * S), (0, 0, 30))
    rh, rv, co = rope_h(), rope_v(), corner()
    # a sample frame: top band, left band, corner at the joint
    for i in range(30):
        blit(im, rh, (6 + i*TILE_W) * S, 6 * S, S)
        blit(im, rh, (6 + i*TILE_W) * S, 40 * S, S)
    for j in range(4):
        blit(im, rv, 6 * S, (6 + j*TILE_W) * S, S)
        blit(im, rv, 239 * S, (6 + j*TILE_W) * S, S)
    for x, y in [(2, 2), (2, 36), (120, 2), (120, 36), (235, 2), (235, 36)]:
        blit(im, co, x * S, y * S, S)
    draw_text(im, "THE PARTY MAKES CAMP...", 8, 60 * S, "#55FF55", S)
    draw_text(im, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", 8, 75 * S, "#55FFFF", S)
    draw_text(im, "0123456789 .,:'!?/()&<>-", 8, 90 * S, "#FF55FF", S)
    draw_text(im, "5,7 E 23:44 CAMPING", 8, 105 * S, "#55FF55", S)
    p = os.path.join(OUT, "_ui_art_proof.png")
    im.save(p)
    print("proof:", p, im.size)

def emit_js():
    art = {
        "pal": PAL,
        "ropeH": {"w": TILE_W, "h": T, "px": rope_h()},
        "ropeV": {"w": T, "h": TILE_W, "px": rope_v()},
        "corner": {"w": 9, "h": 9, "px": corner()},
        "font": {ch: rows for ch, rows in FONT.items()},
    }
    p = os.path.join(OUT, "ui_art.js")
    with open(p, "w") as f:
        f.write("// generated by analysis/make_ui_art.py — original UI art (rope border, ornaments, bitmap font)\n")
        f.write("const UI_ART=" + json.dumps(art, separators=(",", ":")) + ";\n")
    print("js:", p, os.path.getsize(p), "bytes")

proof()
emit_js()

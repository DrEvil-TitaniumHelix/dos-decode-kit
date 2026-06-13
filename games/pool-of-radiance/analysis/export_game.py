import os, struct, json, base64, io, sys
sys.path.insert(0, r".\kit")
from PIL import Image
import dax
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\reproduction"
os.makedirs(OUT, exist_ok=True)
EGA=dax.EGA16

def sprite_dataurl(block, width=None, transparent0=True, scale=1, crop=None):
    w,h,px = dax.decode_image(block["data"], width)
    im=Image.new("RGBA",(w,h),(0,0,0,0))
    for i,p in enumerate(px):
        x=i%w; y=i//w
        if y>=h: break
        if transparent0 and p==0: continue
        r,g,b=EGA[p]; im.putpixel((x,y),(r,g,b,255))
    if crop: im=im.crop(crop)
    if scale>1: im=im.resize((im.width*scale,im.height*scale),Image.NEAREST)
    buf=io.BytesIO(); im.save(buf,"PNG")
    return "data:image/png;base64,"+base64.b64encode(buf.getvalue()).decode(), im.width, im.height

# 1) ALL dungeon levels from GEO1-8.
# CRACKED FORMAT (validated vs Cluebook Podol Plaza, neighbor redundancy 480/480):
# payload = u16 size + 4 planes of 256 bytes over a 16x16 map:
#   plane0: hi nibble = NORTH wall texture, lo = EAST
#   plane1: hi nibble = SOUTH wall texture, lo = WEST (mirrors neighbors exactly)
#   plane2/3: per-cell extra data (floor/decor/event — not yet mapped)
def to_walls(cells):
    # plane0=N/E walls, plane1=S/W walls, plane2=per-cell backdrop/texture id (the author's
    # finite-texture-set: 0x00=open, 0x8x=building-wall variants, 0x0B=alt ground),
    # plane3=feature/event flags.
    w=[]
    for y in range(16):
        row=[]
        for x in range(16):
            i=y*16+x
            b0=cells[i]; b1=cells[256+i]; t=cells[512+i]; f=cells[768+i]
            row.append({"n":b0>>4,"e":b0&0xF,"s":b1>>4,"w":b1&0xF,"t":t,"f":f})
        w.append(row)
    return w
levels=[]
for gi in range(1,9):
    fn=os.path.join(GAME,f"GEO{gi}.DAX")
    if not os.path.exists(fn): continue
    for blk in dax.read_dax(fn):
        d=blk["data"]
        if len(d)>=1026:
            levels.append({"name":f"GEO{gi} #{blk['id']}","walls":to_walls(d[2:2+1024])})
walls=levels[0]["walls"]   # default level for compatibility

# 2) Party roster from CHRDATA*.SAV (fields decoded by cross-record diff)
ABIL=["STR","INT","WIS","DEX","CON","CHA"]
THIEF=["PickPockets","OpenLocks","FindTraps","MoveSilent","HideShadows","HearNoise","ClimbWalls"]
def infer_class(st,exstr,thief_present,items=None,grp=None):
    # CHRDATA off 284 = AD&D class GROUP: 9=Warrior, 6=Priest, 12=Rogue/Mage (decoded).
    # Finer class within a group from thief-skills + decoded equipment + exceptional STR.
    items=items or []
    txt=" ".join(items).lower()
    arcane = st["INT"]>=15
    martial = any(w in txt for w in("sword","flail","mace","hammer","halberd")) and "mail" in txt
    if grp==6:  return "Cleric"
    if grp==12: return "Thief" if thief_present else "Magic-User"
    if grp==9:                                  # warrior group (decoded)
        if exstr>0: return "Fighter"            # exceptional STR = pure-fighter focus
        if st["INT"]>=16 and martial: return "Fighter/Magic-User"   # high INT, no exstr -> multiclass (inferred)
        return "Fighter"
    # fallback (no group byte): old stat/equipment heuristic
    if thief_present: return "Thief"
    if martial and arcane: return "Fighter/Magic-User"
    if exstr>0: return "Fighter"
    if st["WIS"]>=16 and st["WIS"]>st["INT"]: return "Cleric"
    if arcane: return "Magic-User"
    return "Fighter"
import re as _ire
def parse_items(path):
    """Extract equipment from CHRDATA*.ITM — 63-byte records, Pascal-string name at start."""
    if not os.path.exists(path): return []
    raw=open(path,"rb").read(); REC=63; out=[]
    for off in range(0,len(raw)-1,REC):
        ln=raw[off]
        if 2<=ln<=24 and off+1+ln<=len(raw):
            s=raw[off+1:off+1+ln].decode("latin1","ignore").strip()
            s=_ire.sub(r"^(Yes|No)\s+","",s).strip()   # drop readied flag, keep quantities
            if s and any(c.isalpha() for c in s) and s not in out: out.append(s)
    return out
party=[]
for n in range(1,7):
    p=os.path.join(GAME,f"CHRDATA{n}.SAV")
    if not os.path.exists(p): continue
    b=open(p,"rb").read()
    ln=b[0]; name=b[1:1+ln].decode("latin1","ignore").strip()
    stats=dict(zip(ABIL,list(b[16:22])))
    exstr=b[22]; hp=b[50]; thief=list(b[119:126]); tp=any(thief)
    items=parse_items(os.path.join(GAME,f"CHRDATA{n}.ITM"))
    grp=b[284]   # decoded AD&D class group
    party.append({"name":name,"stats":stats,"exstr":exstr,"hp":hp,
                  "thief":dict(zip(THIEF,thief)) if tp else None,
                  "items":items,"cls":infer_class(stats,exstr,tp,items,grp)})

# 3) Sprites: portraits (CHEAD) + combat bodies (CBODY)
chead=dax.read_dax(os.path.join(GAME,"CHEAD.DAX"))
cbody=dax.read_dax(os.path.join(GAME,"CBODY.DAX"))
portraits=[]
for blk in chead[:8]:
    url,w,h=sprite_dataurl(blk, scale=3)
    portraits.append({"id":blk["id"],"url":url,"w":w*3,"h":h*3})
combat=[]
for blk in cbody[:24]:
    url,w,h=sprite_dataurl(blk, width=24, scale=3, crop=(0,1,24,24))
    combat.append({"id":blk["id"],"url":url,"w":24*3,"h":23*3})

# 4) Monster sprites from CPIC (combat creatures), base frames only (id<128)
monsters=[]
seen=set()
for fn in ["CPIC1.DAX","CPIC2.DAX","CPIC3.DAX"]:
    for blk in dax.read_dax(os.path.join(GAME,fn)):
        if blk["id"]<128 and (fn,blk["id"]) not in seen:
            seen.add((fn,blk["id"]))
            url,w,h=sprite_dataurl(blk, width=24, scale=3, crop=(0,1,24,40))
            monsters.append({"src":fn[:-4],"id":blk["id"],"url":url,"w":w,"h":h})
        if len(monsters)>=24: break
    if len(monsters)>=24: break

# 4b) Loot table from ITEM1-4.DAX (the dungeon treasure database, 63-byte records)
loot=[]
for fn in ["ITEM1.DAX","ITEM2.DAX","ITEM3.DAX","ITEM4.DAX"]:
    pth=os.path.join(GAME,fn)
    if not os.path.exists(pth): continue
    for blk in dax.read_dax(pth):
        data=blk["data"]
        for off in range(0,len(data)-1,63):
            ln=data[off]
            if 2<=ln<=24 and off+1+ln<=len(data):
                s=data[off+1:off+1+ln].decode("latin1","ignore").strip()
                s=_ire.sub(r"^(Yes|No)\s+","",s).strip()
                if s and any(c.isalpha() for c in s) and s not in loot: loot.append(s)

# 5) Curated real strings from the GAME.OVR 858-string pool (UI/flavor)
import re as _re
ovr_bytes=open(os.path.join(GAME,"GAME.OVR"),"rb").read()
pool={}
p=0
while p<len(ovr_bytes)-1:
    n=ovr_bytes[p]
    if 6<=n<=64 and p+1+n<=len(ovr_bytes):
        s=ovr_bytes[p+1:p+1+n]
        if all(32<=c<127 for c in s):
            pool[p]=s.decode()
    p+=1
# keep nicely word-like strings (mostly letters/spaces), de-dup, skip credits
JUNK=('memory','exiting','created by','programming','graphic','encoding','manager','ssi',
      'jim ward','cook','winter','breault','special projects','version','overlay')
def good(s):
    if not s or '$' in s or len(s)<8: return False
    low=s.lower()
    if any(j in low for j in JUNK): return False
    letters=sum(c.isalpha() or c==' ' for c in s)
    if letters/len(s)<0.85 or len(s.split())<2: return False
    VOCAB=(' the ',' you',' your',' to ',' of ',' and ',' a ',' is ',' are ',' will ',
           'press','cast','spell','attack','door','gold','party','level','enter','exit',
           'hit','damage','save','dead','poison','treasure','magic','fight','search','combat')
    pad=' '+low+' '
    return any(v in pad for v in VOCAB)
flavor=[]
seen_s=set()
for off,s in pool.items():
    s2=s.strip()
    # drop if it's a substring of one we already kept (overlap artifacts)
    if good(s2) and s2.lower() not in seen_s and not any(s2.lower() in k for k in seen_s):
        seen_s.add(s2.lower()); flavor.append(s2)
flavor=flavor[:80]

# 6) Wall texture decoded from 8X8D (4bpp linear EGA, 8-byte header) — pick a masonry 16x16
def wall_texture():
    d8=dax.read_dax(os.path.join(GAME,"8X8D1.DAX"))[0]["data"][8:]
    W=16; px=[]
    for byte in d8: px.append(byte>>4); px.append(byte&0xF)
    rows=len(px)//W; best=None
    for top in range(0,rows-16):
        cnt={}
        for r in range(top,top+16):
            for c in range(W): v=px[r*W+c]; cnt[v]=cnt.get(v,0)+1
        grey=cnt.get(7,0)+cnt.get(8,0); blk=cnt.get(0,0)
        bad=sum(cnt.get(k,0) for k in (13,9,12,6,11,10,14))
        sc=grey*2+blk-bad*3+(40 if blk>8 and grey>20 else 0)
        if best is None or sc>best[0]: best=(sc,top)
    top=best[1]
    im=Image.new("RGB",(16,16))
    for r in range(16):
        for c in range(16): im.putpixel((c,r),EGA[px[(top+r)*W+c]])
    b=io.BytesIO(); im.save(b,"PNG")
    return "data:image/png;base64,"+base64.b64encode(b.getvalue()).decode()
def tile_dataurl(d8, W, top, size=16):
    px=[]
    for byte in d8: px.append(byte>>4); px.append(byte&0xF)
    im=Image.new("RGB",(size,size))
    for r in range(size):
        for c in range(size): im.putpixel((c,r),EGA[px[(top+r)*W+(c%W)]])
    b=io.BytesIO(); im.save(b,"PNG")
    return "data:image/png;base64,"+base64.b64encode(b.getvalue()).decode()

# Floor texture: a darker/earthy 16x16 from the same 8X8D masonry sheet.
def floor_texture():
    d8=dax.read_dax(os.path.join(GAME,"8X8D1.DAX"))[0]["data"][8:]
    W=16; px=[]
    for byte in d8: px.append(byte>>4); px.append(byte&0xF)
    rows=len(px)//W; best=None
    for top in range(0,rows-16):
        cnt={}
        for r in range(top,top+16):
            for c in range(W): v=px[r*W+c]; cnt[v]=cnt.get(v,0)+1
        earth=cnt.get(6,0)+cnt.get(8,0)+cnt.get(0,0)        # brown/dark-grey/black
        bad=sum(cnt.get(k,0) for k in (13,9,12,11,14,15))
        sc=earth-bad*3
        if best is None or sc>best[0]: best=(sc,top)
    return tile_dataurl(d8,W,best[1])
wallTex=wall_texture()
floorTex=floor_texture()

# REAL wall/floor textures assembled from the decoded 8X8D wall-tile set + WALLDEF usage.
# Tile 13 = the dominant masonry stone block (247 uses in WALLDEF1#1); build a seamless
# stone panel from the gray wall tiles, plus a street/floor tile.
def tileset_8x8(block_id=1):
    td=[b for b in dax.read_dax(os.path.join(GAME,"8X8D1.DAX")) if b["id"]==block_id][0]["data"][9:]
    px=[]
    for by in td: px.append(by>>4); px.append(by&0xF)
    def tile(idx): return [px[idx*64+i] if idx*64+i<len(px) else 0 for i in range(64)]
    return tile
def panel_dataurl(tile, layout):
    th=len(layout); tw=len(layout[0]); im=Image.new("RGB",(tw*8,th*8))
    for ty,row in enumerate(layout):
        for tx,idx in enumerate(row):
            g=tile(idx)
            for i in range(64): im.putpixel((tx*8+i%8, ty*8+i//8), EGA[g[i]])
    b=io.BytesIO(); im.save(b,"PNG")
    return "data:image/png;base64,"+base64.b64encode(b.getvalue()).decode()
T=tileset_8x8(1)
# wall: tile 13 = the game's actual diagonal-beveled masonry (the WALLDEF front-wall surface).
# 2x2 keeps the consistent bevel direction the original uses.
wallTile=panel_dataurl(T, [[13,13],[13,13]])
# street/floor: tile 17 flat stone paving (distinct from the beveled walls)
floorTile=panel_dataurl(T, [[17,17],[17,17]])
# single beveled stone tile for vertical-strip perspective mapping
wallStrip=panel_dataurl(T, [[13]])

# ---- REAL WALLDEF front-wall faces (byte-exact tile composition) ----
# Combined 8X8D tile index: block1=0-69, block3=70-139, block5=140-209 (cracked from the
# WALLDEF face tile refs that exceed 70).
def combined_tiles(fileid=1):
    bs=dax.read_dax(os.path.join(GAME,f"8X8D{fileid}.DAX"))
    sets={b["id"]:b["data"][9:] for b in bs if b["id"] in (1,3,5)}
    tiles=[]
    for bid in (1,3,5):
        if bid not in sets: break
        px=[]
        for by in sets[bid]: px.append(by>>4); px.append(by&0xF)
        for t in range(70): tiles.append([px[t*64+i] if t*64+i<len(px) else 0 for i in range(64)])
    return tiles
def walldef_faces(fileid=1, blockid=1):
    wd=[b for b in dax.read_dax(os.path.join(GAME,f"WALLDEF{fileid}.DAX")) if b["id"]==blockid][0]["data"]
    starts=[p+3 for p in range(len(wd)-3) if wd[p]==1 and wd[p+1]==1 and wd[p+2]==1 and wd[p+3] in (40,18)]
    faces=[]
    for s in starts:
        rows=[]; i=s
        while i<len(wd) and wd[i]==40:
            j=i+1; row=[]
            while j<len(wd) and wd[j]!=39 and j<i+9: row.append(wd[j]); j+=1
            rows.append(row); i=j+1
        if len(rows)>=4 and max(len(r) for r in rows)>=5: faces.append(rows)
    return faces
def face_dataurl(tiles, rows, transp=True):
    h=len(rows); w=max(len(r) for r in rows)
    im=Image.new("RGBA",(w*8,h*8),(0,0,0,0))
    for ry,row in enumerate(rows):
        for rx,t in enumerate(row):
            if not (0<=t<len(tiles)): continue
            g=tiles[t]
            for i in range(64):
                v=g[i]
                if transp and (v==0 or v==13): continue   # black & magenta = transparent opening
                im.putpixel((rx*8+i%8, ry*8+i//8), EGA[v]+(255,))
    b=io.BytesIO(); im.save(b,"PNG")
    return "data:image/png;base64,"+base64.b64encode(b.getvalue()).decode(), im.width, im.height
def classify(tiles, rows):
    used=set(t for r in rows for t in r)
    if used & {6,7,8,9,10,11}: return "door"           # wood door planks (WALLDEF1#1 @685)
    if used & {50,51}: return "gate"                   # portcullis / gate frame (@373)
    if used & {46,47,66}: return "window"              # window/grate facade (@217)
    if used & {59,60,61,33,34}: return "base"          # wall with base ledge / waterline (@61)
    return "plain"
CT=combined_tiles(1)
wfaces={}
for rows in walldef_faces(1,1):
    kind=classify(CT,rows)
    if kind not in wfaces: wfaces[kind]=face_dataurl(CT,rows, transp=(kind!="plain"))
wallFaceDoor   = (wfaces.get("door")   or [None])[0]
wallFaceWindow = (wfaces.get("window") or [None])[0]
wallFaceGate   = (wfaces.get("gate")   or [None])[0]
wallFaceBase   = (wfaces.get("base")   or [None])[0]
wallFacePlain  = (wfaces.get("plain")  or [None])[0]

# 7) REAL decoded ECL area text (from the cracked 6-bit codec) keyed by level name
area_text={}
atp=os.path.join(os.path.dirname(__file__),"ecl_area_text.json")
if os.path.exists(atp):
    rawat=json.load(open(atp))
    def display_ok(s):
        return bool(_ire.match(r"^[A-Z][A-Za-z'\".,!?\- ]{6,}[A-Za-z'\".!?]$", s)) and \
               sum(c.isalpha() or c in " ',.!?\"-" for c in s)/len(s)>0.95 and len(s)>=16
    for k,arr in rawat.items():
        clean=[s for s in arr if display_ok(s)][:10]
        if clean: area_text[k]=clean

# 8) Faithful-UI art: character HEAD portraits (w44), TITLE screen (320), PIC scenes (w88)
def chunky_url(d, w, hskip, scale=1, transparent=False, crop=None):
    body=d[hskip:]; pxs=[]
    for byte in body: pxs.append(byte>>4); pxs.append(byte&0xF)
    h=(len(pxs)+w-1)//w
    im=Image.new("RGBA",(w,h),(0,0,0,0))
    for i,p in enumerate(pxs):
        if i//w<h and (p!=0 or not transparent): im.putpixel((i%w,i//w),EGA[p]+(255,))
    if crop: im=im.crop(crop)
    if scale>1: im=im.resize((im.width*scale,im.height*scale),Image.NEAREST)
    b=io.BytesIO(); im.save(b,"PNG"); return "data:image/png;base64,"+base64.b64encode(b.getvalue()).decode(), im.width, im.height
# Portraits: HEAD*.DAX = 4bpp chunky, 44 BYTES/row = 88 px wide x 40 tall (header bleeds row 0).
# (Cracked 2026-06-12 via vertical-correlation width sweep; the earlier 44px read was half-width.)
heads=[]
for n in range(1,9):
    p=os.path.join(GAME,f"HEAD{n}.DAX")
    if os.path.exists(p):
        for blk in dax.read_dax(p):
            u,w,h=chunky_url(blk["data"],88,8,crop=(0,1,88,41)); heads.append({"url":u,"w":w,"h":h})
        if len(heads)>=8: break
# TITLE: 320x200 4bpp chunky, but the bitmap is circularly rolled left by 12px (DRAGONS(R) wraps
# to the left edge); roll it back so the AD&D logo + copyright lines sit centered.
def title_dataurl(roll=12):
    d=dax.read_dax(os.path.join(GAME,"TITLE.DAX"))[0]["data"][8:]
    px=[]
    for byte in d: px.append(byte>>4); px.append(byte&0xF)
    w,h=320,200
    im=Image.new("RGB",(w,h))
    for y in range(h):
        for x in range(w):
            i=y*w+((x+roll)%w)
            if i<len(px): im.putpixel((x,y),EGA[px[i]])
    b=io.BytesIO(); im.save(b,"PNG")
    return "data:image/png;base64,"+base64.b64encode(b.getvalue()).decode()
title_url=title_dataurl()
scenes=[]
for blk in dax.read_dax(os.path.join(GAME,"PIC1.DAX"))[:4]:
    u,w,h=chunky_url(blk["data"],88,6,crop=(0,0,88,88)); scenes.append({"url":u})

# THE REAL SSI FONT — 8X8D1.DAX block 201: 1bpp 8x8 glyphs in the engine's 6-bit
# charset order (0='@', 1-26=A-Z, 27-31=[\]^_, 32=space, 33-63=!..?; 64+ = Espruar
# runes + UI pieces). Same charset the ECL text codec uses.
fontblk=[b for b in dax.read_dax(os.path.join(GAME,"8X8D1.DAX")) if b["id"]==201][0]["data"]
font64=[list(fontblk[i*8:i*8+8]) for i in range(64)]

data={"ega":EGA,"walls":walls,"levels":levels,"party":party,"portraits":portraits,
      "font64":font64,
      "heads":heads,"titleScreen":title_url,"scenes":scenes,
      "combat":combat,"monsters":monsters,"strings":flavor,"loot":loot,"wallTex":wallTex,"floorTex":floorTex,
      "wallTile":wallTile,"floorTile":floorTile,"wallStrip":wallStrip,
      "wallFaceDoor":wallFaceDoor,"wallFaceWindow":wallFaceWindow,"wallFaceGate":wallFaceGate,
      "wallFaceBase":wallFaceBase,"wallFacePlain":wallFacePlain,
      "areaText":area_text,
      "mapName":"GEO1 / block 18 (decoded dungeon level)"}
with open(os.path.join(OUT,"game_data.js"),"w") as f:
    f.write("// Auto-generated from decoded Pool of Radiance assets (decode-kit)\n")
    f.write("const GAME_DATA = "+json.dumps(data)+";\n")
print(f"wrote game_data.js: {len(levels)} levels, {len(party)} party, {len(monsters)} monsters, {len(flavor)} strings")
print("party:", [(p['name'],p['cls']) for p in party])
print("sample strings:", flavor[:6])

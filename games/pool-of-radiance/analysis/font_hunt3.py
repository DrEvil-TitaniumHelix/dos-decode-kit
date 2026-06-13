import os
from PIL import Image
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\extracted_assets"
# Comprehensive 8x8 font scan, byte-granular. Strong signature:
#  - char 0x20 (space) = 8 zero bytes
#  - chars 0x30-0x39 (digits) and 0x41-0x5A (A-Z) each have ink in 4..7 rows
#  - char 0x49 'I' thin (low ink), 0x4D 'M'/0x57 'W' wide (high ink)
#  - the row just below baseline often blank
def score(buf, base):
    if base<0 or base+0x80*8>len(buf): return -1
    if any(buf[base+0x20*8:base+0x20*8+8]): return -1
    def ink(c):
        g=buf[base+c*8:base+c*8+8]; return sum(bin(b).count('1') for b in g), sum(1 for b in g if b)
    s=0
    for c in list(range(0x30,0x3a))+list(range(0x41,0x5b)):
        bits,rows=ink(c)
        if 6<=bits<=40 and 3<=rows<=8: s+=1
    # M/W should be inkier than I
    iI=ink(0x49)[0]; iM=ink(0x4D)[0]; iW=ink(0x57)[0]
    if iM>iI and iW>iI: s+=4
    return s
def render(buf, base):
    im=Image.new("RGB",(16*9,6*9),(15,15,30))
    for c in range(0x20,0x80):
        g=buf[base+c*8:base+c*8+8]; cxp=((c-0x20)%16)*9; cyp=((c-0x20)//16)*9
        for r in range(8):
            for col in range(8):
                if g[r]&(0x80>>col): im.putpixel((cxp+col,cyp+r),(245,245,220))
    return im.resize((16*9*3,6*9*3),Image.NEAREST)
allc=[]
for fn in ["START.EXE","GAME.OVR"]:
    buf=open(os.path.join(GAME,fn),"rb").read()
    cands=[]
    for b in range(0,len(buf)-0x680):
        sc=score(buf,b)
        if sc>=28: cands.append((sc,b,fn,buf))
    cands.sort(reverse=True)
    # dedup nearby
    seen=[]; top=[]
    for sc,b,f,bb in cands:
        if all(abs(b-x)>32 for x in seen): seen.append(b); top.append((sc,b,f,bb))
        if len(top)>=4: break
    allc+=top
    print(f"{fn}: {len(cands)} raw hits, top: {[(s,hex(b)) for s,b,_,_ in top]}")
# montage top candidates
if allc:
    ims=[render(bb,b) for sc,b,f,bb in allc[:6]]
    Wd=max(i.width for i in ims); Hd=sum(i.height for i in ims)+20*len(ims)
    sheet=Image.new("RGB",(Wd,Hd),(40,40,50))
    from PIL import ImageDraw; dr=ImageDraw.Draw(sheet); y=0
    for (sc,b,f,bb),im in zip(allc[:6],ims):
        sheet.paste(im,(0,y+16)); dr.text((2,y),f"{f} @{hex(b)} score {sc}",fill=(255,255,0)); y+=im.height+20
    sheet.save(os.path.join(OUT,"_font3.png")); print("saved _font3.png")

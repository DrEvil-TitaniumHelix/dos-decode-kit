import os, sys
sys.path.insert(0, r".\kit")
import dax
from PIL import Image, ImageDraw, ImageFont
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\reproduction"
EGA=dax.EGA16
def chunky(d,w,hskip=8,transparent=False):
    body=d[hskip:]; px=[]
    for b in body: px.append(b>>4); px.append(b&0xF)
    h=(len(px)+w-1)//w
    im=Image.new("RGBA",(w,h),(0,0,0,0))
    for i,p in enumerate(px):
        if i//w<h and (p!=0 or not transparent): im.putpixel((i%w,i//w),EGA[p]+(255,))
    return im
# --- build a 320x200 Gold Box screen, scaled to 640x400 (4:3-ish), then to display size ---
SCR=Image.new("RGB",(320,200),(0,0,0))
dr=ImageDraw.Draw(SCR)
# rope border: red/orange double line with gold corners (recreation)
def rope(x0,y0,x1,y1):
    for (a,c) in [(0,(168,0,0)),(1,(255,85,85)),(2,(168,0,0))]:
        dr.rectangle([x0+a,y0+a,x1-a,y1-a],outline=c)
    for cx,cy in [(x0,y0),(x1-3,y0),(x0,y1-3),(x1-3,y1-3)]:
        dr.rectangle([cx,cy,cx+3,cy+3],fill=(255,255,85))
rope(0,0,319,199)
# left picture window (a decoded PIC treasure scene) with inner border
pic=chunky(dax.read_dax(os.path.join(GAME,"PIC1.DAX"))[0]["data"],88,hskip=6)
pic=pic.crop((0,0,88,88))
rope(8,8,8+96,8+96)
SCR.paste(pic.convert("RGB"),(12,12))
# right roster panel
font=ImageFont.load_default()
def txt(x,y,s,col): dr.text((x,y),s,fill=col,font=font)
txt(120,12,"NAME",(255,255,255)); txt(250,12,"AC",(255,255,255)); txt(290,12,"HP",(255,255,255))
party=[("THRENDER GRONE","FTR",4,11),("BAKSHI","FTR",4,7),("RHIANNON","F/M",6,7),
       ("BROTHER SEAN","CLR",5,10),("DARKSTAR","M-U",9,5),("PHINEAS","THF",7,6)]
y=24
for n,c,ac,hp in party:
    txt(120,y,f"{n} {c}",(85,255,255)); txt(252,y,str(ac),(85,255,255)); txt(290,y,str(hp),(85,255,255)); y+=11
# status + message (green) and command bar (magenta)
txt(120,150,"1,1  POOL OF RADIANCE  THE SLUMS",(85,255,85))
txt(8,170,"THE PLAZA AHEAD IS CROWDED WITH MONSTERS.",(85,255,85))
txt(8,182,"HOW WILL YOU PROCEED?",(85,255,85))
txt(8,192,"BOLD  DISGUISE  SNEAK",(255,85,255))
SCR.resize((960,600),Image.NEAREST).save(os.path.join(OUT,"_faithful_mock.png"))
print("saved _faithful_mock.png")

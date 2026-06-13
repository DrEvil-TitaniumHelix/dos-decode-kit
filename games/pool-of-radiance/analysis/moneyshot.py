import os, sys
sys.path.insert(0, r".\kit")
import dax
from PIL import Image, ImageDraw, ImageFont
GAME=r".\games\pool-of-radiance\extracted\poolrad"
OUT =r".\games\pool-of-radiance\reproduction"
EGA=dax.EGA16
blk=dax.read_dax(os.path.join(GAME,"CBODY.DAX"))[0]["data"]
def render(w,scale):
    body=blk[4:]; px=[]
    for byte in body: px.append(byte>>4); px.append(byte&0xF)
    h=(len(px)+w-1)//w
    im=Image.new("RGB",(w,h),(0,0,0))
    for i,p in enumerate(px):
        if i//w<h: im.putpixel((i%w,i//w),EGA[p])
    return im.resize((w*scale,h*scale),Image.NEAREST)
wrong=render(13,11)   # wrong width -> sheared noise
right=render(24,11)   # correct width -> clean knight
# compose side-by-side panel, 1280x720-ish, dark bg
W,H=1280,720
canvas=Image.new("RGB",(W,H),(12,12,18)); dr=ImageDraw.Draw(canvas)
def paste_center(im,cx,top):
    canvas.paste(im,(cx-im.width//2,top))
paste_center(wrong, W//4, 170); paste_center(right, 3*W//4, 150)
# labels
try: fontB=ImageFont.truetype("arialbd.ttf",54); fontS=ImageFont.truetype("arialbd.ttf",30)
except: fontB=ImageFont.load_default(); fontS=fontB
def ctext(s,cx,y,f,col):
    w=dr.textlength(s,font=f); dr.text((cx-w/2,y),s,font=f,fill=col)
ctext("WRONG WIDTH", W//4, 60, fontB, (230,60,50))
ctext("noise", W//4, 120, fontS, (150,150,160))
ctext("RIGHT WIDTH", 3*W//4, 60, fontB, (90,210,90))
ctext("a knight, straight from the 1988 binary", 3*W//4, 120, fontS, (200,200,210))
# arrow
dr.line([(W//2-30,360),(W//2+30,360)],fill=(255,210,70),width=6)
dr.polygon([(W//2+30,348),(W//2+55,360),(W//2+30,372)],fill=(255,210,70))
canvas.save(os.path.join(OUT,"_moneyshot.png"))
print("saved _moneyshot.png", canvas.size)

import os, sys, re
sys.path.insert(0, r".\kit")
import dax
GAME=r".\games\pool-of-radiance\extracted\poolrad"
def item_names(data):
    out=[]; REC=63
    for off in range(0,len(data)-1,REC):
        ln=data[off]
        if 2<=ln<=24 and off+1+ln<=len(data):
            s=data[off+1:off+1+ln].decode("latin1","ignore").strip()
            s=re.sub(r"^(Yes|No)\s+","",s).strip()
            if s and any(c.isalpha() for c in s): out.append(s)
    return out
allitems=[]
for fn in ["ITEM1.DAX","ITEM2.DAX","ITEM3.DAX","ITEM4.DAX"]:
    p=os.path.join(GAME,fn)
    if not os.path.exists(p): continue
    for e in dax.read_dax(p):
        for it in item_names(e["data"]):
            if it not in allitems: allitems.append(it)
print(f"{len(allitems)} unique loot items decoded:")
for it in allitems: print("  ",it)

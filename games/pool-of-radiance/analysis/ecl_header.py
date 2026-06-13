import os, sys, struct
sys.path.insert(0, r".\kit")
import dax
GAME=r".\games\pool-of-radiance\extracted\poolrad"
# Compare the first 32 bytes of several ECL blocks to find the header pattern.
for fn,bid in [("ECL1.DAX",0),("ECL1.DAX",1),("ECL3.DAX",0),("ECL5.DAX",0)]:
    blocks=dax.read_dax(os.path.join(GAME,fn))
    e=blocks[bid]; d=e["data"]
    print(f"\n=== {fn} id={e['id']} len={len(d)} ===")
    print("  hex: "+" ".join(f"{x:02X}" for x in d[:28]))
    # hypothesis: header = WORD count, then count x WORD offsets? or records of 4 bytes
    w0=struct.unpack_from("<H",d,0)[0]
    print(f"  word[0]=0x{w0:04X}={w0}")
    # how many leading 4-byte records have bytes[2]==0x01? (the XX YY 01 ?? pattern)
    n=0; recs=[]
    while n*4+4<=len(d):
        a,b,c,e2=d[n*4],d[n*4+1],d[n*4+2],d[n*4+3]
        if c==0x01: recs.append((a|(b<<8),e2)); n+=1
        else: break
    print(f"  leading records with [2]==01: {len(recs)} -> {[f'{v:04X}/{t}' for v,t in recs]}")

import struct
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ex=open(GAME+r"\START.EXE","rb").read()
OVR_SIZE=206105

# find all CD 3F
hits=[]
i=ex.find(b"\xCD\x3F")
while i!=-1:
    hits.append(i); i=ex.find(b"\xCD\x3F",i+1)
hs=set(hits)
# entry runs: sequences spaced 5 bytes
runs=[]
for h in hits:
    if h-5 not in hs and h+5 in hs:  # run start
        n=1; p=h
        while p+5 in hs: p+=5; n+=1
        runs.append((h,n))
print(f"entry runs found: {len(runs)}")
for h,n in runs[:8]:
    pre=ex[h-32:h]
    print(f"\nrun@0x{h:05X} ({n} entries); 32 bytes BEFORE:")
    print("   "+" ".join(f"{x:02X}" for x in pre))
    print(f"   first entries: "+" ".join(f"{x:02X}" for x in ex[h:h+15]))

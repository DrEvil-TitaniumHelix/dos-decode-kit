import struct
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ex=open(GAME+r"\START.EXE","rb").read()
ovr=open(GAME+r"\GAME.OVR","rb").read()
OVRLEN=len(ovr)

# Overlay segment headers: CD 3F 00 00 <dword fileoff> <w codesize> <w fixupsize> <w nentry>
segs=[]
i=0
while i < len(ex)-12:
    if ex[i]==0xCD and ex[i+1]==0x3F and ex[i+2]==0x00 and ex[i+3]==0x00:
        foff,csize,fxsize,nent=struct.unpack_from("<IHHH",ex,i+4)
        # sanity: file offset within OVR, plausible sizes
        if 0 < foff < OVRLEN and 0 < csize < 0x10000 and nent < 400:
            stub_seg=(i-0x200)//16
            segs.append(dict(file=i,seg=stub_seg,ovr_off=foff,csize=csize,fx=fxsize,nent=nent))
    i+=1
print(f"overlay segments found: {len(segs)}")
print(f"{'stubseg':>8}{'ovr_off':>9}{'+codesz':>9}{'end':>9}{'fixup':>7}{'entries':>8}")
tot_code=0; tot_ent=0
segs.sort(key=lambda s:s["ovr_off"])
for s in segs:
    end=s["ovr_off"]+s["csize"]
    tot_code+=s["csize"]; tot_ent+=s["nent"]
    print(f"  0x{s['seg']:04X}{s['ovr_off']:9d}{s['csize']:9d}{end:9d}{s['fx']:7d}{s['nent']:8d}")
print(f"\n{len(segs)} units; total overlaid code={tot_code} bytes (OVR={OVRLEN}); total public entry points={tot_ent}")
# coverage check: do segments tile GAME.OVR?
covered=sum(s["csize"] for s in segs)
print(f"coverage: {covered}/{OVRLEN} = {100*covered/OVRLEN:.0f}% of GAME.OVR is mapped overlaid code")
import json
json.dump(segs, open("overlay_segmap.json","w"), indent=1)
print("wrote overlay_segmap.json")

import json
segmap=json.load(open(r".\games\pool-of-radiance\analysis\overlay_segmap.json"))
# segmap entries have seg (paragraph), ovr_off (file offset of unit), csize, etc.
# A far-call seg:off where seg is an overlay unit seg -> file offset = unit ovr_off + off
# Build seg->entry
bysem={}
for e in segmap:
    bysem.setdefault(e["seg"],[]).append(e)
targets=[0x709,0xba,0xb0,0x3d0,0x3ca,0x3f1,0x78,0x7c,0x802,0x464,0x3d3]
for t in targets:
    e=bysem.get(t)
    print("seg 0x%X:"%t, "FOUND units="+str([(x["ovr_off"]) for x in e]) if e else "NOT in segmap (resident START.EXE: fileoff=0x200+seg*16+off)")
# Print a few segmap entries to see fields
print("sample:",segmap[0])
print("total segs:",sorted(set(e['seg'] for e in segmap)))

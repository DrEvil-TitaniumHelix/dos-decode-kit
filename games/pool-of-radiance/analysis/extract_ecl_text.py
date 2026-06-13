import os, sys, json, re
sys.path.insert(0, r".\kit")
import dax, ecl_textcodec as T
GAME=r".\games\pool-of-radiance\extracted\poolrad"
WORDS=re.compile(r"\b(THE|YOU|YOUR|AND|ARE|WITH|HAVE|THIS|THAT|WILL|HERE|FROM|INTO|THEY|HAS|FOR|NOT|ALL|ONE|WHO|OUT|MONSTERS|PARTY|DOOR|ROOM|GOLD|ATTACK|MAGIC|MAN|WAND|AUCTION)\b")
def clean(strs):
    out=[]; seen=set()
    for s in strs:
        s=s.strip().rstrip("B@[]\^_(")  # trim common trailing artifact chars
        s=s.strip()
        if not (14<=len(s)<=160): continue
        letters=sum(c.isalpha() or c in " ',.!?-\"" for c in s)
        if letters/len(s)<0.92: continue
        vowels=sum(c in "AEIOU" for c in s)
        if vowels/max(1,sum(c.isalpha() for c in s))<0.22: continue
        if len(WORDS.findall(s))<2: continue        # require >=2 real words
        m=re.search(r"[A-Z]", s)              # trim leading junk to first capital
        if m: s=s[m.start():]
        m2=re.search(r'[.!?\"](?=[^.!?]*$)', s)  # trim trailing junk after last sentence end
        if m2: s=s[:m2.end()]
        s=s.strip()
        if len(WORDS.findall(s))<2: continue
        k=re.sub(r"[^A-Za-z]","",s).upper()[:30]
        if k in seen: continue
        seen.add(k); out.append(s)
    return out
area_text={}; total=0
for i in range(1,9):
    p=os.path.join(GAME,f"ECL{i}.DAX")
    if not os.path.exists(p): continue
    for e in dax.read_dax(p):
        raw=[s for (pos,s) in T.scan_strings(e["data"], min_len=14)]
        good=clean(raw)
        if good: area_text[f"GEO{i} #{e['id']}"]=good; total+=len(good)
print(f"areas with text: {len(area_text)}; total clean strings: {total}")
print("\nGEO1 #18 sample:")
for s in area_text.get("GEO1 #18",[])[:8]: print("  ",repr(s))
print("\nGEO3 #0 sample:")
for s in area_text.get("GEO3 #0",[])[:4]: print("  ",repr(s))
json.dump(area_text, open("ecl_area_text.json","w"))
print("\nwrote ecl_area_text.json")

import struct, json
from collections import Counter
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ovr=open(GAME+r"\GAME.OVR","rb").read()
ex=open(GAME+r"\START.EXE","rb").read()
segs=json.load(open("overlay_segmap.json"))
md=Cs(CS_ARCH_X86,CS_MODE_16)

# Pull the Pascal string pool from GAME.OVR front (length-prefixed) with file offsets
strings={}  # offset -> text
i=8  # after FBOV + size
# scan whole file for length-prefixed printable runs >=4
def scan_pstrings(buf):
    out={}
    p=0
    while p<len(buf)-1:
        n=buf[p]
        if 4<=n<=80 and p+1+n<=len(buf):
            s=buf[p+1:p+1+n]
            if all(32<=c<127 for c in s):
                out[p]=s.decode()
        p+=1
    return out
pstr=scan_pstrings(ovr)
# index by raw substring presence for crude per-unit role hints: which keywords appear in each unit's data window? 
# Strings live in a shared pool; instead, classify by KEYWORDS found anywhere, then map the biggest units via entrypoint disasm.
KW={'combat':['attack','hit','damage','armor','weapon','melee','missile'],
    'magic':['spell','magic','cast','cleric','wizard','memoriz'],
    'char':['strength','dexterity','constitution','intelligence','wisdom','charisma','level','experience','hit points'],
    'menu':['exit','done','yes','no','press','choose','select','option'],
    'dungeon':['door','wall','search','north','south','east','west','area','secret'],
    'item':['gold','sword','armor','potion','scroll','ring','shield','treasure'],
    'town':['shop','train','temple','tavern','vault','buy','sell','pool of radiance']}
allstr=" | ".join(s.lower() for s in pstr.values())
print("string-pool keyword presence (whole game):")
for cat,kws in KW.items():
    found=[k for k in kws if k in allstr]
    print(f"  {cat:8s}: {found}")
print(f"\ntotal pascal strings recovered: {len(pstr)}")
print("sample strings:")
for off in list(pstr)[:0]: pass
import itertools
shown=0
for off,s in pstr.items():
    if len(s)>=12 and shown<25:
        print(f"  0x{off:05X}: {s!r}"); shown+=1

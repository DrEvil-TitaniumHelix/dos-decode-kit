import os, sys
sys.path.insert(0, r".\kit")
import dax
GAME=r".\games\pool-of-radiance\extracted\poolrad"
d=dax.read_dax(os.path.join(GAME,"ECL1.DAX"))[0]["data"]
# Hypothesis A: strings are printable runs ending in a byte with high bit set (char|0x80)
def hibit_strings(buf, minlen=4):
    out=[]; cur=[]
    for b in buf:
        c=b&0x7F
        if 0x20<=c<0x7e:
            cur.append(chr(c))
            if b&0x80:                 # terminator
                if len(cur)>=minlen: out.append(''.join(cur))
                cur=[]
        else:
            cur=[]
    return out
sA=hibit_strings(d)
print(f"Hypothesis A (high-bit terminator): {len(sA)} strings")
for s in sA[:12]: print("   ",repr(s))
# Hypothesis B: text section at end of block. Show last 200 bytes masked 0x7F
print("\nLast 160 bytes (masked 0x7F):")
tail=bytes(x&0x7F for x in d[-160:])
print("   ",''.join(chr(x) if 32<=x<127 else '.' for x in tail))
# Hypothesis C: byte histogram - is there a printable-heavy region?
import collections
print("\nByte ranges by 512-chunk (printable% after mask 0x7F):")
for i in range(0,len(d),512):
    seg=d[i:i+512]; pr=sum(1 for x in seg if 0x20<=(x&0x7f)<0x7f)/len(seg)
    print(f"   0x{i:04X}: {pr*100:3.0f}% printable")

import sys, os, glob, collections, pickle
sys.path.insert(0, r'.\kit')
import dax
files = sorted(glob.glob(r".\games\pool-of-radiance\extracted\poolrad\ECL*.DAX"))
print("ECL files:", [os.path.basename(f) for f in files])
allblocks = []
for f in files:
    try:
        bl = dax.read_dax(f)
        for e in bl:
            allblocks.append((os.path.basename(f), e["id"], e["data"]))
    except Exception as ex:
        print("ERR", f, ex)
print("total blocks", len(allblocks))
freq = collections.Counter()
for fn, bid, d in allblocks:
    for b in d[20:]:
        freq[b] += 1
print("top bytes:", [(hex(k), v) for k, v in freq.most_common(20)])
pickle.dump(allblocks, open(r".\games\pool-of-radiance\analysis\allblocks.pkl", "wb"))

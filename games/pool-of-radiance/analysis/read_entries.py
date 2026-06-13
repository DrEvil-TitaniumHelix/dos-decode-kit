import json, struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ovr=open(GAME+r"\GAME.OVR","rb").read()
md=Cs(CS_ARCH_X86,CS_MODE_16)
led={r["unit"]:r for r in json.load(open("unit_ledger.json"))}

# For a unit, disasm the first ~12 insns of each (real) entry point; collect far-call segs + immediates
def analyze_unit(stubseg, maxentries=6):
    u=led[stubseg]; base=u["ovr_off"]
    print(f"\n##### UNIT 0x{stubseg:04X}  ovr@{base} size={u['csize']} funcs={u['nfuncs']} entries={u['nentry']} #####")
    eo=sorted(e for e in u["entries"] if e < u["csize"]-8)  # drop the trailing trap
    for off in eo[:maxentries]:
        fo=base+off
        print(f"  -- entry +0x{off:04X} (file 0x{fo:05X}):")
        cnt=0
        for ins in md.disasm(ovr[fo:fo+60],fo):
            print(f"       {ins.mnemonic:6s} {ins.op_str}")
            cnt+=1
            if cnt>=10 or ins.mnemonic in('ret','retf'): break
for seg in [0x38,0x86,0x25]:
    analyze_unit(seg,5)

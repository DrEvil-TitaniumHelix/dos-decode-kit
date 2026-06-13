import struct, re
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
md=Cs(CS_ARCH_X86, CS_MODE_16)

# GAME.OVR structure
ov=open(GAME+r"\GAME.OVR","rb").read()
print(f"GAME.OVR {len(ov)} bytes. first32:", " ".join(f"{x:02X}" for x in ov[:32]))
print("isMZ:", ov[:2]==b"MZ")
strings=re.findall(rb"[\x20-\x7e]{5,}", ov)
print(f"{len(strings)} ascii strings. sample:", [s.decode()[:40] for s in strings[:12]])

# Disassemble START.EXE entry to prove we can read coherent code
ex=open(GAME+r"\START.EXE","rb").read()
hdr_para=struct.unpack_from("<H",ex,8)[0]; code0=hdr_para*16
ip,cs=struct.unpack_from("<HH",ex,20)
entry_file=code0+cs*16+ip
print(f"\n=== START.EXE disasm @ entry (file 0x{entry_file:X}) ===")
for ins in list(md.disasm(ex[entry_file:entry_file+80], entry_file))[:24]:
    print(f"  {ins.address:06X}: {ins.mnemonic:7s} {ins.op_str}")

print(f"\n=== GAME.OVR disasm @ 0x0 (raw code guess) ===")
start=0 if ov[:2]!=b"MZ" else struct.unpack_from('<H',ov,8)[0]*16
for ins in list(md.disasm(ov[start:start+80], start))[:24]:
    print(f"  {ins.address:06X}: {ins.mnemonic:7s} {ins.op_str}")

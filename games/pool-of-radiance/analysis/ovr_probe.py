import struct
GAME=r".\games\pool-of-radiance\extracted\poolrad"
for fn in ["START.EXE","GAME.OVR"]:
    b=open(f"{GAME}\{fn}","rb").read()
    print(f"\n=== {fn}  {len(b)} bytes ===")
    print("first 32:", " ".join(f"{x:02X}" for x in b[:32]))
    if b[:2]==b"MZ":
        e_cblp,e_cp,e_crlc,e_cparhdr=struct.unpack_from("<HHHH",b,2)
        ip,cs=struct.unpack_from("<HH",b,20)  # e_ip, e_cs at 0x14,0x16
        e_lfarlc=struct.unpack_from("<H",b,24)[0]
        hdr_para=struct.unpack_from("<H",b,8)[0]
        last,pages=struct.unpack_from("<HH",b,2)
        load_size=(pages-1)*512+(last if last else 512)
        print(f"  MZ: header_paras={hdr_para} (=0x{hdr_para*16:X} bytes), entry CS:IP={cs:04X}:{ip:04X}, reloc@{e_lfarlc} count={e_crlc}")
        print(f"  pages={pages} last={last} load_module≈{load_size} code_start=0x{hdr_para*16:X}")
    else:
        print("  not MZ — raw overlay or custom container")
        # entropy-ish: count printable strings
        import re
        strings=re.findall(rb"[\x20-\x7e]{5,}", b)
        print(f"  {len(strings)} ascii strings; sample:", [s.decode()[:30] for s in strings[:8]])

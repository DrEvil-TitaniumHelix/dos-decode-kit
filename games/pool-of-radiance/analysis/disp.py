from capstone import Cs, CS_ARCH_X86, CS_MODE_16
GAME=r".\games\pool-of-radiance\extracted\poolrad"
ov=open(GAME+r"\GAME.OVR","rb").read()
md=Cs(CS_ARCH_X86, CS_MODE_16)
# dispatch @0x3C73. Walk the cmp al,imm / jne / push cs / call handler chain to get exact opcode->handler
addr=0x3C73
end=0x3F00
cur=None
out=[]
for ins in md.disasm(ov[addr:end-addr+addr], addr):
    m=ins.mnemonic; o=ins.op_str
    if m=="cmp" and o.startswith("al,"):
        cur=int(o.split(",")[1],16)
    elif m=="call" and cur is not None:
        tgt=ins.op_str
        out.append((cur,tgt))
    if ins.address>0x3EB0: break
# Just dump cmp/call/jne around opcodes 0x14-0x18
for ins in md.disasm(ov[0x3C73:0x3DB0], 0x3C73):
    if ins.mnemonic in ("cmp","jne","je","jbe","jae","call","jmp"):
        print(f"  {ins.address:06X}: {ins.mnemonic} {ins.op_str}")

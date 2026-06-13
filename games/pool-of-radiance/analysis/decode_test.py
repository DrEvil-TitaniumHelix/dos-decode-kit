import sys
sys.path.insert(0, 'kit')
import dax, struct
from collections import Counter

base = 'games/pool-of-radiance/extracted/poolrad/'
allblocks = []
for n in range(1, 9):
    for b in dax.read_dax(base + f'ECL{n}.DAX'):
        allblocks.append((n, b['id'], b['data']))

# Insight: in the byte stream, sequences "01 D2 6D", "01 82 6E", "01 79 6E", "01 7E 6E"
# appear. 0x6Dxx/0x6Exx = game-state variable addresses. So 0x01 is an ARG-MARKER:
# 0x01 <WORD addr> = a "variable reference" argument.
# 0x09 <WORD val>  = "immediate constant" argument? (0x09 00 0B 01 ...)
# 0x03 <WORD addr> = another arg type.
# These are ARGUMENT tokens, not full instructions. The instruction = opcode then args.
#
# Re-examine ECL2 id9 start: A7 A0 | 0C 00 3F 00 02 00 3F 3A 0D 3A 0D | 13 ...
#   A7 A0 = 0xA0A7 = addr 41127->byteoff... = pointer header? Actually first 2 bytes look like a GOTO addr.
# The first WORD of bytecode = a jump target (the "default handler" begins with a forward jump
# to skip the data/handlers). Let's treat byte0..1 as a WORD pointer and see where it lands.

for n, bid, d in allblocks[:8]:
    bc = d[20:]
    w = struct.unpack_from('<H', bc, 0)[0]
    bo = (w & 0x7FFF) - 5000
    print(f"ECL{n} id{bid}: first WORD=0x{w:04X} -> byteoff {bo} (len {len(bc)}) inrange={0<=bo<len(bc)}")

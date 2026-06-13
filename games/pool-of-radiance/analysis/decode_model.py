# Model of text decompressor at GAME.OVR 0x8626, char map 0x7BA6.
# Variables (bp-relative):
#  [bp-1] = i (count of input bytes consumed)
#  [bp+8] = nbytes (total input bytes)
#  [bp-6] = phase (1..4)
#  [bp-3] = cur byte, [bp-4] = prev byte
#  [bp-5] = extracted 6-bit char code
#  char 0 => skip (string terminator within block / padding)
#  decoded char = c+0x40 if c<=0x1f else c
def chmap(c):
    return (c + 0x40) & 0xFF if c <= 0x1f else c

def decode_string(buf, pos, nbytes):
    # emulate loop @0x8645
    out = []
    i = 0
    phase = 1
    cur = 0
    prev = 0
    p = pos
    while i < nbytes:
        # @0x8650: if phase < 4: fetch next byte (advance PC), shift window
        if phase < 4:
            # inc PC; prev=cur(old [bp-3] copied to [bp-4]); fetch new cur; i++
            prev = cur
            cur = buf[p]; p += 1
            i += 1
        # compute char by phase
        if phase == 1:
            c = (cur >> 2) & 0xFF
        elif phase == 2:
            dx = (cur >> 2) & 0xFF
            ax = ((prev << 6) + dx) & 0xFF
            c = (ax >> 2) & 0xFF
        elif phase == 3:
            dx = (cur >> 4) & 0xFF
            ax = ((prev << 4) + dx) & 0xFF
            c = (ax >> 2) & 0xFF
        elif phase == 4:
            c = cur & 0x3f
        # advance phase 1->2->3->4->1
        if phase < 4:
            phase += 1
        else:
            phase = 1
        if c == 0:
            continue
        out.append(chmap(c))
    # tail @0x875f: if phase==4 handle last char
    return bytes(out)

if __name__ == '__main__':
    import sys; sys.path.insert(0,r'.\kit'); import dax, os
    GAME=r'.\games\pool-of-radiance\extracted\poolrad'
    d=dax.read_dax(os.path.join(GAME,'ECL1.DAX'))[0]['data']
    # brute: try every position, decode 30 bytes, look for english
    import re
    best=[]
    for pos in range(0, len(d)-40):
        s=decode_string(d,pos,30)
        # count letters/spaces
        txt=bytes(b if 0x20<=b<0x7f else 0x2e for b in s)
        words=len(re.findall(rb'[A-Za-z]{3,}', s))
        if words>=4:
            best.append((words,pos,txt))
    best.sort(reverse=True)
    for w,pos,txt in best[:20]:
        print('pos=0x%04X w=%d : %s'%(pos,w,txt.decode('latin1')))

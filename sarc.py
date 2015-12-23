# {enemy,fighter,assistpokemon/item_,stage}
import sys, struct, zlib, subprocess, os
print 'Getting strings...'
outdir = sys.argv[3]
if not os.path.exists(outdir):
    os.mkdir(outdir)
strs = subprocess.check_output(['strings', '-', sys.argv[2]]).rstrip().split('\n')
by_crc = {}
def try_crc(str):
    crc = zlib.crc32(str) & 0xffffffff
    by_crc.setdefault(crc, set()).add(str)


fp = open(sys.argv[1], 'rb')
assert fp.read(4) == 'SARC'
num_files, = struct.unpack('<I', fp.read(4))
for i in xrange(num_files):
    print i
    fp.seek(0x10 + 0x10 * i)
    crc, off, flags, size = struct.unpack('<IIII', fp.read(16))
    fp.seek(off)
    compressed = fp.read(size)
    print hex(flags)
    data = zlib.decompress(compressed)
    offset = struct.unpack('<I', data[0xC0:0xC4])[0]
    name = data[offset:offset+data[offset:].find('\0')].decode("utf-8") 
    print(name)
    
    try_crc('fighter/' + name)
    try_crc('stage/final/' + name)
    try_crc('stage/' + name)
    try_crc('menu/' + name)
    try_crc('enemy/' + name)
    try_crc('minigame/' + name)
    try_crc('assistpokemon/' + name)
    
    strings = by_crc.get(crc, set())
    print strings
    #continue
    if len(strings) >= 2:
        raise Exception('Multiple CRC possibilities for %08x' % crc)
    elif len(strings) == 1:
        fn = strings.pop()
        assert not fn.startswith('/')
        outfn = os.path.join(outdir, fn)
        if not os.path.exists(os.path.dirname(outfn)):
            os.makedirs(os.path.dirname(outfn))
    else:
        outfn = os.path.join(outdir, 'unkcrc-%08x-%s' % (crc, name))
 
    open(outfn, 'wb').write(data)


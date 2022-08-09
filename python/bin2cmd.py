
# Convert from binary image file + origin address + execute address to
# trs-80 command file (/CMD)

import sys

binfilename = sys.argv[1]
origin = int(sys.argv[2],16)
execute = int(sys.argv[3],16)

with open(binfilename, 'rb') as f:
    x = f.read()
    s = len(x)
    p = 0
    cmdfilename = binfilename.split('.')[0] + '.cmd'
    with open(cmdfilename,'wb') as fout:
        while s > 256:
            fout.write(b'\x01\x02')
            fout.write(origin.to_bytes(2,'little'))
            for i in range(0,256):
                fout.write(x[p].to_bytes(1, 'little'))
                p += 1
            s -= 256
            origin += 256
        if s > 0:
            fout.write(b'\x01')
            fout.write((s+2).to_bytes(1, 'little'))
            fout.write(origin.to_bytes(2,'little'))
            for i in range(0,s):
                fout.write(x[p].to_bytes(1, 'little'))
                p += 1
        fout.write(b'\x02\x02')
        fout.write(execute.to_bytes(2,'little'))

            
        
    


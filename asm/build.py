import os
import sys

if __name__ == "__main__":
    if len(sys.argv) == 1 or len(sys.argv) > 2:
        print(f'Usage: {sys.argv[0]} <target>')
        os.sys.exit(-1)
    basename = sys.argv[1]

    print(f'Assembling render.asm...')
    cmd = f'tools\\asz80.exe -o -p -s -l render.asm'
    #print(cmd)
    rv = os.system(cmd)
    if rv != 0:
        print("ERROR: Assembly failed.")
        os.sys.exit(-1)

    print(f'Linking render.s19...')
    cmd = f'tools\\aslink.exe -m -p -s render.rel -u'
    #print(cmd)
    rv = os.system(cmd)
    if rv != 0:
        print("ERROR: Linking failed.")
        os.sys.exit(-1)

    print(f'Generating render.bin...')
    cmd = f'tools\\srec2bin -q -o 5300 -f 00 render.s19 render.bin'
    #print(cmd)
    rv = os.system(cmd)
    if rv != 0:
        print("ERROR: Conversion to binary failed.")
        os.sys.exit(-1)

    print(f'Generating {basename}.bin...')
    cmd = f'python \\romtools\\romjoin.py {basename}.bin render.bin ..\\python\\{basename}.dat'
    #print(cmd)
    rv = os.system(cmd)
    if rv != 0:
        print("ERROR: romjoin failed.")
        os.sys.exit(-1)

    print(f'Generating {basename}.cmd...')
    cmd = f'python ..\\python\\bin2cmd.py {basename}.bin 5300 5300'
    #print(cmd)
    rv = os.system(cmd)
    if rv != 0:
        print("ERROR: Conversion to cmd failed.")
        os.sys.exit(-1)

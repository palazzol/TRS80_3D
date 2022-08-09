
python ..\python\3d80.py -c testcode.asm
tools\asz80.exe -o -p -s -l sample.asm
tools\aslink.exe -m -p -s sample.rel -u
tools\srec2bin -a 5300 sample.s19 sample.bin
tools\srec_cat.exe sample.bin -binary -output sample.hex -Intel -address-length=2 -output_block_size=16
python ..\python\bin2cmd.py sample.bin 5300 5300

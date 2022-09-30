
tools\asz80.exe -o -p -s -l render.asm
tools\aslink.exe -m -p -s render.rel -u
tools\srec2bin -o 5300 render.s19 render.bin
tools\srec_cat.exe render.bin -binary -output render.hex -Intel -address-length=2 -output_block_size=16
python \romtools\romjoin.py full.bin render.bin ..\python\data.bin
python ..\python\bin2cmd.py full.bin 5300 5300

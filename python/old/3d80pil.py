# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 12:45:59 2021

@author: frank
"""

from PIL import Image
from PIL import ImageDraw

class Display:
    
    images = {}
    images_alt = {}
    
    def __init__(self):
        with open('..\\roms\\8044316a.u36','rb') as f:
            charrom = f.read(0x800)
        addr = 0
        for i in range(0,0x100):
            im = Image.new('1',(8,24))
            for j in range(0,8):
                x = charrom[addr]
                addr+=1
                for k in range(0,8):
                    bit = (x>>(7-k))&1
                    im.putpixel((k,j*2),bit)
                    im.putpixel((k,j*2+1),bit)
            if i<128:
                self.images[i] = im
                self.images_alt[i] = im
            elif i<192:
                self.images[i+64] = im
            else:
                self.images_alt[i] = im
                
        for i in range(128,192):
            im = Image.new('1',(8,24))
            draw = ImageDraw.Draw(im, '1')
            for j in range(0,6):
                bit = (i>>j)&1
                if bit==1:
                    draw.rectangle((0+(j%2*4),0+(j//2)*8,3+(j%2*4),7+(j//2)*8),fill=1)
            self.images[i] = im
            self.images_alt[i] = im
                
        self.im = Image.new('1',(512,384))
        for i in range(0,64):
            self.im.paste(self.images[i],box=((i%64)*8,0))
            self.im.paste(self.images[i+64],box=((i%64)*8,24))
            self.im.paste(self.images[i+128],box=((i%64)*8,48))
            self.im.paste(self.images[i+192],box=((i%64)*8,72))
        self.im.show()
    
    def write(self, addr, data):
        addr2 = addr-0x3c00
        self.im.paste(self.images[data],box=((addr2%64)*8,(addr2//64)*24))

    def read(self, addr):
        pass
    def set(self,x,y):
        pass
    def reset(self,x,y):
        pass
    def cls(self):
        for addr in range(0x3c00,0x4000):
            self.write(addr,0x20)
        self.im.show()
    def enaltset(self, tf):
        pass
    
test = Display()
test.cls()


  

    
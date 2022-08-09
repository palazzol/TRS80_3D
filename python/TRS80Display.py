# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 12:45:59 2021

@author: frank
"""

import pygame
import sys
import collections

class TRS80Display:
    
    altset = False
    images = {}
    images_alt = {}
    screen = None
    raster = None
    vram = {}
    dirty = {}
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((2*(512+100),2*(384+100)))
        self.screen.fill((0, 0, 0))
        self.raster = pygame.Surface((512+100,384+100), flags=0, depth=8)
        self.raster.fill((0, 0, 0))
        self.raster.convert(self.screen)
        pygame.display.set_caption("TRS-80 Model III gfx simulator")

        # Initialize character-based surface arrays
        with open('8044316a.u36','rb') as f:
            charrom = f.read(0x800)
            
        # create the character rom surfaces
        addr = 0
        for i in range(0,0x100):
            im = pygame.Surface((8, 24), flags=0, depth=8)
            for j in range(0,8):
                x = charrom[addr]
                addr+=1
                for k in range(0,8):
                    bit = (x>>(7-k))&1
                    im.set_at((k,j*2),bit*255)
                    im.set_at((k,j*2+1),bit*255)
            im.convert(self.screen)
            if i<128:
                self.images[i] = im
                self.images_alt[i] = im
            elif i<192:
                self.images[i+64] = im
            else:
                self.images_alt[i] = im

        # create the graphics character surfaces
        for i in range(128,192):
            im = pygame.Surface((8, 24), flags=0, depth=8)
            for j in range(0,6):
                bit = (i>>j)&1
                if bit==1:
                    im.fill(255, rect=(0+((j%2)*4),0+(j//2)*8,4,8))
            im.convert(self.screen)
            self.images[i] = im
            self.images_alt[i] = im
        # initialize videoram
        self.cls()
        
    def update(self):
        self.raster2 = pygame.transform.scale(self.raster, (2*(512+100),2*(384+100)))
        self.screen.blit(self.raster2,(0,0))
        pygame.display.flip()
        
    def write(self, addr, data):
        self.writenu(addr,data)
        self.update()
        
    def writenu(self, addr, data):
        if addr in self.vram:
            if self.vram[addr] != data:
                self.vram[addr] = data
        else:
            self.vram[addr] = data
        addr2 = addr-0x3c00
        row = addr2//64
        col = addr2%64
        if self.altset:
            self.raster.blit(self.images_alt[data],(col*8+50,row*24+50))
        else:
            self.raster.blit(self.images[data],(col*8+50,row*24+50))

    def read(self, addr):
        return self.vram[addr]
    
    def setnu(self,x,y):
        col = x//2
        row = y//3
        addr = 0x3c00+row*64+col
        bit = (x%2)+(y%3)*2
        z = self.read(addr)
        if z<128 or z>191:
            z = 128
        z = (0x80 | (z&0x3f) | (1<<bit))
        self.writenu(addr, z)
        
    def set(self,x,y):
        self.setnu(x,y)
        self.update()

    def resetnu(self,x,y):
        col = x//2
        row = y//3
        addr = 0x3c00+row*64+col
        bit = (x%2)+(y%3)*2
        z = self.read(addr)
        if z<128 or z>191:
            z = 128
        z = (0x80 | (z&0x3f) & (0x3f-(1<<bit)))
        self.writenu(addr, z)
    
    def reset(self,x,y):
        self.resetnu(x,y)
        self.update()
        
    def cls(self):
        self.clsnu()
        self.update()
        
    def clsnu(self):
        for addr in range(0x3c00,0x4000):
            self.writenu(addr,0x20)
        self.update()
        
    def enaltset(self, tf):
        self.altset = tf
        for addr in range(0x3c00,0x4000):
            data = self.read(addr)
            if data>191:
                self.writenu(addr,data)
        self.update()
    
    def pause(self):
        while True:
            self.checkexit()
    def checkexit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
                
    def drawline(self,x0,y0,x1,y1):
        self.drawlinenu(x0,y0,x1,y1)
        self.update()

    def drawlinenu(self,x0,y0,x1,y1):
        dx =  abs(x1-x0)
        if x0<x1:
            sx=1
        else:
            sx=-1
        dy = -abs(y1-y0)
        if y0<y1:
            sy=1
        else:
            sy=-1
        err = dx+dy
        while True:
            self.setnu(x0, y0)
            if (x0 == x1 and y0 == y1):
                break
            e2 = 2*err
            if (e2 >= dy):
                err += dy
                x0 += sx
            if (e2 <= dx):
                err += dx
                y0 += sy
        
    def printat(self,row,col,s):
        self.printatnu(row,col,s)
        self.update()
        
    def printatnu(self,row,col,s):
        addr = 0x3c00+row*64+col
        for i in range(len(s)):
            self.writenu(addr,ord(s[i]))
            addr+=1
            if addr>0x3fff:
                break
        
    def save(self,filename):
        pygame.image.save(self.screen, filename)

    def freeze(self):
        self.vram_save = self.vram.copy()
        
    def changes(self):
        raddr = []
        rdata = []
        for addr in range(0x3c00, 0x3fff):
            if self.vram[addr] != self.vram_save[addr]:
                raddr.append(addr)
                rdata.append(self.vram[addr])
        self.freeze()
        return raddr, rdata
        
if __name__ == "__main__":
    import time
    
    d = TRS80Display()
    
    # test print
    d.printat(0,32-6,"Hello TRS-80!")
    s = ''
    for i in range(0,255):
        s+=chr(i)
    d.printat(1,0,s)
    time.sleep(1)
    d.save('..\\images\\printtest.jpg')
    
    # test enaltset
    d.enaltset(True)
    d.save('..\\images\\alttest.jpg')
    time.sleep(1)
    d.enaltset(False)
    
    # test line drawing
    d.drawline(0,15,127,15)
    d.drawline(0,47,127,47)
    d.drawline(0,15,0,47)
    d.drawline(127,15,127,47)
    d.drawline(0,15,127,47)
    d.drawline(0,47,127,15)
    d.save('..\\images\\lines.jpg')
    
    d.pause()

    
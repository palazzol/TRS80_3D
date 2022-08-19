# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 14:21:19 2021

@author: frank
"""

import time
import os

def CodeGen(f, name, addr, data):
    table = {}
    for i in range(0,len(data)):
        a = addr[i]
        d = data[i]
        if d in table:
            table[d].append(a)
        else:
            table[d] = [ a ]
    print(name+':', file=f)
    for d in table:
        print("        LD      A,"+hex(d), file=f)
        for a in table[d]:
            print("        LD      ("+hex(a)+"),A", file=f)
    print("        RET", file=f)
    print("", file=f)
        
# convert from homogenous 3D coordinates to 2D pixels
def Convert3Dto2D(clip):
    rv = []
    for i in range(0,np.shape(clip)[1]):
        p = np.array([int(np.round(clip[0,i]/clip[3,i]+64.0)),
                      int(np.round(clip[1,i]/(clip[3,i]*2)+24.0))])
        rv.append(p)
    return rv
    
def RenderFrame(left):
    if left:
        clip = proj.dot(lstack).dot(obj)
        d.printat(0,0,"L")
    else:
        clip = proj.dot(rstack).dot(obj)
        d.printat(0,0,"R")
        
    pixels = Convert3Dto2D(clip)
    for line in obj_linelist:
        d.drawlinenu(pixels[line[0]][0],
                     pixels[line[0]][1],
                     pixels[line[1]][0],
                     pixels[line[1]][1])
    d.update()
    """
    lastp = pixels[0]
    for p in pixels[1:]:
        d.drawlinenu(lastp[0],lastp[1],p[0],p[1])
        lastp = p
    #p = pixels[0]
    #d.drawlinenu(lastp[0],lastp[1],p[0],p[1])
    d.update()
    """

if __name__ == "__main__":
    
    import TRS80Display
    import numpy as np
    import sys
    import argparse

    # Parsing the arguments
    parser = argparse.ArgumentParser(description = '3D80')
    parser.add_argument('-l','--loop',default=False,help='Loop display',required=False,action="store_true")
    parser.add_argument('-m','--movie',default='',help='Render to movie file',required=False)
    parser.add_argument('-c','--code',default='',help='Render to assembly code',required=False)
    global_args = parser.parse_args()

    if global_args.movie:
        import cv2
        
    # Here is the geometric setup
    
    # Assumptions:
    #   Units are "rough horizontal pixel" dimensions, 1in = 16 pixels
    #   User is 2ft from screen, which is object center = 24in*16 = 384units
    #   Can render 8 inches wide, which is 128 units (same as horizontal pixels)
    #   Can render 96 units tall (2x vertical pixels, for proper aspect ratio)
    #   Near clipping plane and far clipping plane are +/-4 inches in/out of the screen
    #   Pupil distance is average - 2.5in = 40 units
    #
    # World coordinates:
    # Camera is at the origin (between the eyes)
    # Scene is along the +Z axis, centered at X,Y,Z = (0,0,384.0)
    # Y is up, X is left
    
    distance = 48
    
    doperspective = True        # Choose Perspective or Planar projection
    
    conversion = 16.0           # units/in
    pupildist = 2.5*conversion  # 2.5in
    mid = distance*conversion         # 24in to screen
    front = (distance-4)*conversion   # near clipping plane             
    rear = (distance+4)*conversion    # far clipping plane
    
    # scale objects differently depending on the projection
    if doperspective:
        #d = 80.0
        d = 60.0
    else:
        #d = 40.0
        d = 30.0
        
    # object is part square and part triangle
    z1 = mid-d # square
    z2 = mid+d # triangle
    """
    obj = np.array([[d,d,z1,1],
              [d,-d,z1,1],
              [-d,-d,z1,1],
              [-d,d,z1,1],
              [d,0,z2,1],
              [-d,-d,z2,1],
              [-d,d,z2,1]]).transpose()
    """
    """
    obj = np.array([[-d,d,z2,1],
                    [d,d,z2,1],
                    [d,-d,z2,1],
                    [-d,-d,z2,1],
                    [-d,d,z2,1],
                    
                    [-d,d,z1,1],
                    [-d,-d,z1,1],
                    [-d,-d,z2,1],
                    
                    [-d,-d,z1,1],
                    [d,-d,z1,1],
                    [d,-d,z2,1],
                    
                    [d,-d,z1,1],
                    [d,d,z1,1],
                    [d,d,z2,1],
                    
                    [d,d,z1,1],
                    [-d,d,z1,1]]).transpose()
    """
    # Nodelist, to be transformed
    obj = np.array(
                   [[-d,d,z2,1],  
                    [d,d,z2,1],   
                    [d,-d,z2,1],  
                    [-d,-d,z2,1], 
                    [-d,d,z1,1],  
                    [-d,-d,z1,1], 
                    [d,-d,z1,1],  
                    [d,d,z1,1]]).transpose()  

    # Wirelist, to be used in rendering
    obj_linelist = np.array(
                   [[0,1],
                    [1,2],
                    [2,3],
                    [3,0],
                    [0,4],
                    [4,5],
                    [5,3],
                    [5,6],
                    [6,2],
                    [6,7],
                    [7,1],
                    [7,4]])

    # Perspective Projection Matrix
    pers = np.array([[1,0,0,0],
                     [0,1,0,0],
                     [0,0,1,0],
                     [0,0,1.0/front,1]])
    
    # Planar projection Matrix
    plan = np.array([[1,0,0,0],
                     [0,1,0,0],
                     [0,0,1,0],
                     [0,0,0,1]])
    
    if doperspective:
        proj = pers
    else:
        proj = plan
    
    # translation matrix from object center to origin (camera)
    t1 = np.array([[1,0,0,0],
                     [0,1,0,0],
                     [0,0,1,-mid],
                     [0,0,0,1]])
    
    # translation matrix from origin (camera) to object center
    t2 = np.array([[1,0,0,0],
                     [0,1,0,0],
                     [0,0,1,mid],
                     [0,0,0,1]])
    
    theta = 15*np.pi/180.0
    s = np.sin(theta)
    c = np.cos(theta)
    
    rotatex = np.array([[1,0,0,0],
                       [0,c,s,0],
                       [0,-s,c,0],
                       [0,0,0,1]])
    
    theta = 15*np.pi/180.0
    s = np.sin(theta)
    c = np.cos(theta)
    
    rotatez = np.array([[c,s,0,0],
                       [-s,c,0,0],
                       [0,0,1,0],
                       [0,0,0,1]])
    
    # rotation matrix around Y axis, theta degrees, from X to Z
    theta = 6*np.pi/180.0
    s = np.sin(theta)
    c = np.cos(theta)
    
    rotate = np.array([[c,0,s,0],
                       [0,1,0,0],
                       [-s,0,c,0],
                       [0,0,0,1]])
    
    # rotation matrix around Y axis, rotate camera around obj from center to left eye pos
    angle = np.arctan2(pupildist,mid)
    c = np.cos(angle)
    s = np.sin(angle)
    
    rotatel = np.array([[c,0,s,0],
                       [0,1,0,0],
                       [-s,0,c,0],
                       [0,0,0,1]])
    
    # rotation matrix around Y axis, rotate camera around obj from center to right eye pos
    rotater = np.array([[c,0,-s,0],
                       [0,1,0,0],
                       [s,0,c,0],
                       [0,0,0,1]])
    
    # distance adjustment - eye position is slightly further away from object than center pos 
    dadj = np.sqrt(mid*mid-pupildist*pupildist)-mid
    
    # translation to back up the camera little
    away = np.array([[1,0,0,0],
                     [0,1,0,0],
                     [0,0,1,dadj],
                     [0,0,0,1]])
    
    # matrix stack, show object from left eye
    # (translate obj to origin, rotate it, put it back, then back it up a touch)
    lstack = away.dot(t2).dot(rotatel).dot(t1)
    #lstack = t2.dot(rotatel).dot(t1)
    
    # matrix stack, show object from right eye
    # (translate obj to origin, rotate it, put it back, then back it up a touch)
    rstack = away.dot(t2).dot(rotater).dot(t1)
    #rstack = t2.dot(rotater).dot(t1)
    
    # rotation matrix to spin the object each frame
    # translate obj to origin, spin it, put it back
    R = t2.dot(rotate).dot(t1)
    
    d = TRS80Display.TRS80Display()
    
    # initial rotation
    Rinit = t2.dot(rotatez).dot(rotatex).dot(t1)
    obj = Rinit.dot(obj)
    # Save this orientation, for multiple render types
    saved_obj = obj.copy()

    # Render movie and exit
    if global_args.movie:
        print('Rendering movie file...')
        obj = saved_obj.copy()
        img_array = []
        for i in range(0,60):
            d.clsnu()
            RenderFrame(True)
            d.save("temp.jpg")
            img = cv2.imread("temp.jpg")
            img_array.append(img)
            d.clsnu()
            RenderFrame(False)
            d.save("temp.jpg")
            img = cv2.imread("temp.jpg")
            img_array.append(img)
            obj = R.dot(obj)
            if d.checkexit():
                print('Operation Aborted')
                os.remove("temp.jpg")
                sys.exit(-1)
        os.remove("temp.jpg")

        height, width, layers = img_array[0].shape
        size = (width,height)
        
        out = cv2.VideoWriter(global_args.movie,cv2.VideoWriter_fourcc(*'DIVX'), 60, size)
        for i in range(len(img_array)):
            out.write(img_array[i])
        out.release()
        print('Done!')
    
    if global_args.code:
        print('Rendering assembly code...')
        with open(global_args.code, 'w') as f:
            obj = saved_obj.copy()
            # Emit One Stereo Frame
            d.clsnu()
            d.freeze()
            RenderFrame(False)
            addr, data = d.changes()
            CodeGen(f,'IFRAME',addr,data)
            #print(len(addr))
            #obj = R.dot(obj)
            for i in range(1,2):
                d.freeze()
                d.clsnu()
                RenderFrame(True)
                addr, data = d.changes()
                CodeGen(f,'LFRAME',addr,data)
                d.freeze()
                d.clsnu()
                RenderFrame(False)
                addr, data = d.changes()
                CodeGen(f,'RFRAME',addr,data)
                #obj = R.dot(obj)
                if d.checkexit():
                    print('Operation Aborted')
                    os.remove(global_args.code)
                    sys.exit(-1)
        print('Done!')

    # Render animation until user exit
    if global_args.loop:
        print('Rendering animation to screen...')
        obj = saved_obj.copy()
        while True:
            d.clsnu()
            RenderFrame(True)
            time.sleep(1/60.0)
            d.clsnu()
            RenderFrame(False)
            time.sleep(1/60.0)
            
            obj = R.dot(obj)
            if d.checkexit():
                print('Done!')
                sys.exit(0)

    """
    # Emit a Stereo movie (not working yet)
    d.clsnu()
    d.freeze()
    RenderFrame(False)
    addr, data = d.changes()
    CodeGen('IFRAME',addr,data)
    #print(len(addr))
    obj = R.dot(obj)
    for i in range(0,72):
        d.freeze()
        d.clsnu()
        RenderFrame(True)
        addr, data = d.changes()
        CodeGen('LFRAME'+str(i),addr,data)
        print()
        d.freeze()
        d.clsnu()
        RenderFrame(False)
        addr, data = d.changes()
        CodeGen('RFRAME'+str(i),addr,data)
        print()
        obj = R.dot(obj)
    """

    """
    # ?????
    d.clsnu()
    RenderFrame(False)
    
    d.freeze()
    d.cls()
    addr, data = d.changes()
    CodeGen('RCLR',addr,data)
        
    d.freeze()
    RenderFrame(True)
    addr, data = d.changes()
    CodeGen('LDRAW',addr,data)
    
    d.freeze()
    d.cls()
    addr, data = d.changes()
    CodeGen('LCLR',addr,data)
    
    d.freeze()
    RenderFrame(False)
    addr, data = d.changes()
    CodeGen('RDRAW',addr,data)
    """

    # TEST CODE
    #d.freeze()
    #d.clsnu()
    #RenderFrame(True)
    #addr, data = d.changes()
    #print(len(addr))

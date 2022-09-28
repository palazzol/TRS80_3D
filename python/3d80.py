# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 14:21:19 2021

@author: frank
"""

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

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

def DataGen(f, name, data):
    print(f"{name}:", file=f)
    for i in range(0, 0x0400, 0x10):
        print("        .db     ", file=f, end='')
        for j in range(0x0f):
            print(f"0x{data[i+j]:02x},", file=f, end='')
        j=j+1
        print(f"0x{data[i+j]:02x}", file=f)

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

def makerot_x(degrees):
    theta = degrees*np.pi/180.0
    s = np.sin(theta)
    c = np.cos(theta)
    return np.array([[1,0,0,0],
                     [0,c,s,0],
                     [0,-s,c,0],
                     [0,0,0,1]])

def makerot_y(degrees):
    # rotation matrix around Y axis, from X to Z
    theta = degrees*np.pi/180.0
    s = np.sin(theta)
    c = np.cos(theta)
    return np.array([[c,0,s,0],
                     [0,1,0,0],
                     [-s,0,c,0],
                     [0,0,0,1]])

def makerot_z(degrees):
    theta = degrees*np.pi/180.0
    s = np.sin(theta)
    c = np.cos(theta)
    return np.array([[c,s,0,0],
                     [-s,c,0,0],
                     [0,0,1,0],
                     [0,0,0,1]])

def maketrans(vector):
    return np.array([[1,0,0,vector[0]*conversion],
                     [0,1,0,vector[1]*conversion],
                     [0,0,1,vector[2]*conversion],
                     [0,0,0,1]])
                     
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
    parser.add_argument('-c2', '--code2', default='', help='Render to assembly code, blit', required=False)
    parser.add_argument('shapefilename', nargs=1)
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
    
    with open(f'{global_args.shapefilename[0]}','rb') as f:
        shape = tomllib.load(f)

    conversion = 16.0           # units/in

    # defaults

    distance_in = 48
    
    perspective = True        # Choose Perspective or Planar projection
    pupildist_in = 2.5        # 2.5in
    frontclip_in = 4
    objscale_in = 3.75

    init_rot_x = 0.0
    init_rot_y = 0.0
    init_rot_z = 0.0

    frame_rot_x = 0.0
    frame_rot_y = 0.0
    frame_rot_z = 0.0

    num_frames = 60

    if 'Camera' in shape:
        camera = shape['Camera']
        if 'distance_in' in camera:
            distance_in = camera['distance_in']
        if 'pupildist_in' in camera:
            pupildist_in = camera['pupildist_in']
        if 'frontclip_in' in camera:
            frontclip_in = camera['frontclip_in']
        if 'perspective' in camera:
            perspective = camera['perspective']
        else:
            # default scale objects differently depending on the projection
            if perspective:
                #objscale_in = 5.0
                objscale_in = 3.75
            else:
                #objscale_in = 2.5
                objscale_in = 1.875
        if 'objscale_in' in camera:
            objscale_in = camera['objscale_in']

    if 'Object' in shape:
        object = shape['Object']
        if 'nodelist' in object:
            nodelist = object['nodelist']
        else:
            print('No nodelist in Object')
            sys.exit(-1)
        if 'linelist' in object:
            linelist = object['linelist']
        else:
            print('No linelist in Object')
            sys.exit(-1)

        if 'init_rot_x' in object:
            init_rot_x = object['init_rot_x']
        if 'init_rot_y' in object:
            init_rot_y = object['init_rot_y']
        if 'init_rot_z' in object:
            init_rot_z = object['init_rot_z']

        if 'frame_rot_x' in object:
            frame_rot_x = object['frame_rot_x']
        if 'frame_rot_y' in object:
            frame_rot_y = object['frame_rot_y']
        if 'frame_rot_z' in object:
            frame_rot_z = object['frame_rot_z']

        if 'num_frames' in object:
            num_frames = object['num_frames']

    else:
        print('No Object in shape file')
        sys.exit(-1)

    pupildist = pupildist_in*conversion
    mid = distance_in*conversion         # 24in to screen
    front = (distance_in-frontclip_in)*conversion   # near clipping plane
    d = objscale_in*conversion

    # Scale, and Transform object to object center 
    for i in range(0,len(nodelist)):
        nodelist[i][0] *= d
        nodelist[i][1] *= d
        nodelist[i][2] *= d
        nodelist[i][2] += distance_in*conversion

    # Nodelist, to be transformed
    obj = []
    for i in range(0,len(nodelist)):
        obj.append([ nodelist[i][0], nodelist[i][1], nodelist[i][2], 1.0 ])
    obj = np.array(obj).transpose()
    
    # Linelist, to be used in rendering
    obj_linelist = np.array(linelist)

    # Perspective Projection Matrix
    pers = np.array([[1,0,0,0],
                     [0,1,0,0],
                     [0,0,1,0],
                     [0,0,1.0/front,0]])
    
    # Planar projection Matrix
    plan = np.array([[1,0,0,0],
                     [0,1,0,0],
                     [0,0,1,0],
                     [0,0,0,1]])
    
    if perspective:
        proj = pers
    else:
        proj = plan
    
    # translation matrix from object center to origin (camera)
    t1 = maketrans([0.0,0.0,-distance_in])

    # translation matrix from origin (camera) to object center
    t2 = maketrans([0.0,0.0,distance_in])
    
    irotatex = makerot_x(init_rot_x)
    irotatey = makerot_y(init_rot_y)
    irotatez = makerot_z(init_rot_z)

    frotatex = makerot_x(frame_rot_x)
    frotatey = makerot_y(frame_rot_y)
    frotatez = makerot_z(frame_rot_z)
    
    # rotation matrix around Y axis, rotate camera around obj from center to left eye pos
    angle = np.arctan2(pupildist,mid)
    rotatel = makerot_y(angle*180.0/np.pi)
    rotater = makerot_y(-angle*180.0/np.pi)
    
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
    R = t2.dot(frotatez).dot(frotatey).dot(frotatex).dot(t1)
    
    d = TRS80Display.TRS80Display()
    
    # initial rotation
    Rinit = t2.dot(irotatez).dot(irotatey).dot(irotatex).dot(t1)
    obj = Rinit.dot(obj)
    # Save this orientation, for multiple render types
    saved_obj = obj.copy()

    # Render movie and exit
    if global_args.movie:
        print('Rendering movie file...')
        obj = saved_obj.copy()
        img_array = []
        for i in range(0,num_frames):
            d.clsnu()
            RenderFrame(True)
            d.save("temp.png")
            img = cv2.imread("temp.png")
            img_array.append(img)
            d.clsnu()
            RenderFrame(False)
            d.save("temp.jpg")
            img = cv2.imread("temp.png")
            img_array.append(img)
            obj = R.dot(obj)
            if d.checkexit():
                print('Operation Aborted')
                os.remove("temp.png")
                sys.exit(-1)
        os.remove("temp.png")

        height, width, layers = img_array[0].shape
        size = (width,height)
        
        out = cv2.VideoWriter(global_args.movie,cv2.VideoWriter_fourcc(*'XVID'), 60, size)
        #out = cv2.VideoWriter(global_args.movie,cv2.VideoWriter_fourcc(*'DIVX'), 60, size)
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

    if global_args.code2:
        print('Rendering assembly code...')
        with open(global_args.code2, 'w') as f:
            obj = saved_obj.copy()
            # Emit One Stereo Frame
            RenderFrame(True)
            data = []
            for i in range(0x3c00, 0x4000):
                data.append(d.vram[i])
            DataGen(f, 'LDATA', data)
            d.freeze()
            d.clsnu()
            RenderFrame(False)
            data = []
            for i in range(0x3c00, 0x4000):
                data.append(d.vram[i])
            DataGen(f, 'RDATA', data)
        print('Done!')

    # Render animation until user exit
    if global_args.loop:
        print('Rendering animation to screen...')
        while True:
            obj = saved_obj.copy()
            for i in range(0,num_frames):
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

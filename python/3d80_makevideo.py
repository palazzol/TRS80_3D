# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 14:21:19 2021

@author: frank
"""

import cv2
import TRS80Display
import time
import numpy as np

x = True
#x = False

front = 320.0
mid = 384.0
rear = 448.0
if x:
    d = 75.0
else:
    d = 40.0
z1 = mid-d # square
z2 = mid+d # triangle
square = np.array([[d,d,z1,1],
          [d,-d,z1,1],
          [-d,-d,z1,1],
          [-d,d,z1,1],
          [d,0,z2,1],
          [-d,-d,z2,1],
          [-d,d,z2,1]]).transpose()

pers = np.array([[1,0,0,0],
                 [0,1,0,0],
                 [0,0,1,0],
                 [0,0,1.0/front,1]])

plan = np.array([[1,0,0,0],
                 [0,1,0,0],
                 [0,0,1,0],
                 [0,0,0,1]])

if x:
    proj = pers
else:
    proj = plan

t1 = np.array([[1,0,0,0],
                 [0,1,0,0],
                 [0,0,1,-mid],
                 [0,0,0,1]])

t2 = np.array([[1,0,0,0],
                 [0,1,0,0],
                 [0,0,1,mid],
                 [0,0,0,1]])

theta = 5*np.pi/180.0
s = np.sin(theta)
c = np.cos(theta)

rotate = np.array([[c,0,s,0],
                   [0,1,0,0],
                   [-s,0,c,0],
                   [0,0,0,1]])

R = t2.dot(rotate).dot(t1)

clip = proj.dot(square)
#print(clip)

answers = []
for i in range(0,np.shape(clip)[1]):
    p = np.array([clip[0,i]/clip[3,i],clip[1,i]/(clip[3,i]*2)])
    #print(p)
    answers.append(p)
    
#print(answers)

d = TRS80Display.TRS80Display()

img_array = []
for i in range(0,72*5):
    d.clsnu()
    firsttime = True
    for p in answers:
        if firsttime:
            firsttime = False
        else:
            d.drawline(int(lastp[0]+64),int(lastp[1]+24),int(p[0]+64),int(p[1]+24))
        lastp = p
    p = answers[0]
    d.drawlinenu(int(lastp[0]+64),int(lastp[1]+24),int(p[0]+64),int(p[1]+24))
    d.update()
    d.save("temp.jpg")
    img = cv2.imread("temp.jpg")
    height, width, layers = img.shape
    size = (width,height)
    img_array.append(img)
    d.checkexit()
    time.sleep(1.0/30)
    square = R.dot(square)
    clip = proj.dot(square)
    answers = []
    for i in range(0,np.shape(clip)[1]):
        p = np.array([clip[0,i]/clip[3,i],clip[1,i]/(clip[3,i]*2)])
        answers.append(p)

out = cv2.VideoWriter('project.avi',cv2.VideoWriter_fourcc(*'DIVX'), 30, size)
 
for i in range(len(img_array)):
    out.write(img_array[i])
out.release()



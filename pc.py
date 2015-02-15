from cv2 import MORPH_RECT

__author__ = 'timur'
import numpy as np
import cv2
import cv2.cv as cv

v = cv2.__version__

print "We work on",v, "version of cv2"

# this part is checking all existing cameras
#for i in range(-10,10):
#    cap = cv2.VideoCapture(i)
#    print i,"input has state",cap.isOpened()

cap = cv2.VideoCapture("MATLAB.avi")
#cap = cv2.VideoCapture(1)#video from webcam

#nFrame = cap.get(cv.CV_CAP_PROP_FRAME_COUNT) #frame number
disk1 = cv2.getStructuringElement(MORPH_RECT,ksize=(5,5))
disk3 = cv2.getStructuringElement(MORPH_RECT,ksize=(15,15))
disk2 = cv2.getStructuringElement(MORPH_RECT,ksize=(23,23))
sum_Up=0
sum_Down=0
List=[]

#print nFrame
while(cap.isOpened()):
    ret, frame = cap.read()
    #print line on video
    #cv2.line(frame,(0,200),(800,200),(255,0,0),4)
    #set custom video input resolution
    #ret = cap.set(3,1280)
    #ret = cap.set(4,720)

    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    cv2.imshow('The window name',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
# take first frame of the video

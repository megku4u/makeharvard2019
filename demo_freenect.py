#!/usr/bin/env python

#############
# Code from: https://github.com/amiller/libfreenect-goodies
#############

"""
Run this code to test that the xbox kinect works properly. If it does, a window
showing the IR and RGB camera data side by side.
"""

from freenect import sync_get_depth as get_depth, sync_get_video as get_video
import cv2
import numpy as np

def doloop():
    global depth, rgb
    while True:
        # Get a fresh frame
        (depth,_), (rgb,_) = kinect_get_depth(), kinect_get_video()

        # Build a two panel color image
        d3 = np.dstack((depth,depth,depth)).astype(np.uint8)
        da = np.hstack((d3,rgb))

        # Simple Downsample
        cv2.imshow('both',np.array(da[::2,::2,::-1]))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print('An error occured with OpenCV')
            break

doloop()

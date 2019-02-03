#!/usr/bin/env python

import cv2
from PIL import Image
import sys
import os
import urllib
import tensorflow.contrib.tensorrt as trt
import tensorflow as tf
import numpy as np
from tf_trt_models.detection import download_detection_model, build_detection_graph
from tf_trt_models.pbtxt_converter import pbtxt_to_dic
from tensorflow.core.framework import graph_pb2 as gpb
from google.protobuf import text_format as pbtf
from freenect import sync_get_depth as kinect_get_depth, sync_get_video as kinect_get_video

#################
"""Detecting Objects in Video Code"""
# Adapting code from the example notebook from repository to work with video
# instead of static images. Imports the dictionary using a function I wrote
# in pbtxt_converter - takes the argument of LABELS_PATH. Displays image
# detection from webcam video feed.

MODEL = 'ssd_mobilenet_v1_coco'
DATA_DIR = '/data/'
CONFIG_FILE = MODEL + '.config'   # ./data/ssd_inception_v2_coco.config
CHECKPOINT_FILE = 'model.ckpt'    # ./data/ssd_inception_v2_coco/model.ckpt
IMAGE_PATH = './data/IMG_5308.jpg'
LABELS_PATH = './data/inception_v2_class_labels.pbtxt'

IR_BOOL=True # if false, the program will only use the rgb camera
#################

def pretty_depth(depth): # function from libfreenect examples
    """Converts depth into a 'nicer' format for display

    This is abstracted to allow for experimentation with normalization

    Args:
        depth: A numpy array with 2 bytes per pixel

    Returns:
        A numpy array that has been processed whos datatype is unspecified
    """
    np.clip(depth, 0, 2**10 - 1, depth)
    depth >>= 2
    depth = depth.astype(np.uint8)
    return depth

def display_webcam():
    # capturing video from camera, storing in 'cap'. 0 selects the camera
    n = 0

    while True:
        sum_image_brightness = 0
        image_brightness = 0
        i = j= counter = 0
        if (n % 25 == 0):
            (frame,_) = kinect_get_video()
            x_dim = frame.shape[0] -1
            y_dim = frame.shape[1] -1
            if i < x_dim:
                if j < y_dim:
                    sum_image_brightness += frame[i][j][counter%3]
                    i += 10
                    j += 10
                    counter += 1
                    print(sum_image_brightness)
            image_brightness = (sum_image_brightness*10)/(counter)
            if image_brightness < 40:
                IR_BOOL = True
            else:
                IR_BOOL = False
        if IR_BOOL == False:
            (frame,_) = kinect_get_video()
        else:
            (depth,_) = kinect_get_depth()
            depth = pretty_depth(depth)
            frame = np.dstack((depth,depth,depth)).astype(np.uint8)

        #################
        """Load image from the frame, resize, and run network"""


        cv2.imshow('Object Detection', frame)
        n += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print('An error occured with OpenCV')
            break
    cap.release()
    cv2.destroyAllWindows()
        #cv2.destroyAllWindows()

if __name__ == "__main__":

    display_webcam()

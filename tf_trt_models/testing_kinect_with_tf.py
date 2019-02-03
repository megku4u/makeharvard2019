#!/usr/bin/env python

"""
Program written by: Duncan Mazza
*(code included from external sources, see below)*

This program enables an XBox Kinect to act as an external camera enabled by
tensorflow object detection software. The program automatically switches the
video source between the Kinect's RGB camera and IR camera depending on how
dark the environment is. The main purpose of the program is to detect how many
people detected in the frame at any given point in time. This number for each
frame is piped into a deque that contains data for the last 10 frames; the
maximum value in the deque is what the program returns.

This program runs using the tf_trt_models software, OpenCV, and libfreenect;
snippets from the git repos of tf_trt_models and libfreenect are used in the
following software.

tf_trt_models: https://github.com/NVIDIA-AI-IOT/tf_trt_models
libfreenect: https://github.com/OpenKinect/libfreenect
"""

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
import random

#################

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

def display_webcam(dictionary):
    # capturing video from camera, storing in 'cap'. 0 selects the camera
    n = 0 # frame counter
    person_list = [0,0,0,0,0,0,0,0,0,0]
    global person_count

    while True:
        sum_image_brightness = 0
        image_brightness = 0
        i=j=counter = 0
        if (n % 25 == 0):
            (frame,_) = kinect_get_video()
            x_dim = frame.shape[0] -1
            y_dim = frame.shape[1] -1
            if i < x_dim:
                if j < y_dim:
                    for k in range(0,2):
                        sum_image_brightness += frame[i][j][k]
                        i += 10
                        j += 10
                        counter += 3
            image_brightness = (sum_image_brightness/(counter))

            if image_brightness < 30:
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

        image = frame

        # for some reason, the resizing isn't working...? I'll just skip the resizing for now
        #image_resized = np.array(image.resize((300, 300)))
        #image_resized = np.resize(image, (300,300))

        scores, boxes, classes, num_detections = tf_sess.run([tf_scores,
                                                             tf_boxes,
                                                             tf_classes,
                                                             tf_num_detections],
                                                             feed_dict=
                                                                {tf_input: image[None, ...]})

        boxes = boxes[0] # index by 0 to remove batch dimension
        scores = scores[0]
        classes = classes[0]
        num_detections = num_detections[0]
        frame_count = 0
        #################
        # Display rectangles on the image

        for i in range(int(num_detections)):
            # scale box to image coordinates
            box = boxes[i] * np.array([image.shape[0], image.shape[1],
                                       image.shape[0], image.shape[1]])

            ###### Display rectangles using OpenCV
            # Format: image,(topleft_x, topleft_y),(bottomright_x, bottomright_y),color,line thickness
            topleft_x = int(box[1])
            topleft_y = int(box[2])
            bottomright_x = int(box[3])
            bottomright_y = int(box[0])
            score = round(scores[i], 2)

            cv2.rectangle(image,(topleft_x, topleft_y),
                          (bottomright_x, bottomright_y),(0, 255, 0),1,8,0)

            font = cv2.FONT_HERSHEY_COMPLEX
            # Dictionary contains classifications associated classes[i]
            dictionary_index = classes[i]
            cv2.putText(image,
                        '({}) {}%'.format(dictionary[dictionary_index],
                        round(scores[i]*100), 4),(topleft_x + 5, topleft_y - 7),
                        font,0.5,(255,255,255), 1, cv2.LINE_AA)
            if dictionary[dictionary_index] == 'person':
                frame_count+=1
            frame_count +=1

        # Displaying the image in a window labeled Object Detection
        cv2.imshow('Object Detection', image)
        n += 1
        person_list.append(frame_count)
        person_list.pop()
        person_count = person_list[0]
        for i in range(1,len(person_list)):
            if person_list[i] > person_list[i-1]:
                person_count = person_list[i]

        print(person_list)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print('An error occured with OpenCV')
            break
    cap.release()
    cv2.destroyAllWindows()
        #cv2.destroyAllWindows()

if __name__ == "__main__":
    config_path, checkpoint_path = download_detection_model(MODEL, 'data')

    frozen_graph, input_names, output_names = build_detection_graph(
        config=config_path,
        checkpoint=checkpoint_path,
        score_threshold=0.5,
        batch_size=1
    )

    print(output_names)
    #################
    # Optimize the model with TensorRT

    trt_graph = trt.create_inference_graph(
        input_graph_def=frozen_graph,
        outputs=output_names,
        max_batch_size=1,
        max_workspace_size_bytes=1 << 25,
        precision_mode='FP16',
        minimum_segment_size=50
    )

    with open('./data/ssd_inception_v2_coco_trt.pb', 'wb') as f:
        f.write(trt_graph.SerializeToString())
    #################

    #################
    #Create session and load graph

    tf_config = tf.ConfigProto()
    tf_config.gpu_options.allow_growth = True

    tf_sess = tf.Session(config=tf_config)

    tf.import_graph_def(trt_graph, name='')

    tf_input = tf_sess.graph.get_tensor_by_name(input_names[0] + ':0')
    tf_scores = tf_sess.graph.get_tensor_by_name('detection_scores:0')
    tf_boxes = tf_sess.graph.get_tensor_by_name('detection_boxes:0')
    tf_classes = tf_sess.graph.get_tensor_by_name('detection_classes:0')
    tf_num_detections = tf_sess.graph.get_tensor_by_name('num_detections:0')
    #################

    # convert the pbtxt file to a python dictionary:
    dictionary = pbtxt_to_dic(LABELS_PATH)
    # run the main function:
    display_webcam(dictionary)

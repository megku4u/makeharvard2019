# makeharvard2019
GitHub repo for the team of Duncan, Katie, Megan, and Florian at MakeHarvard 2019
__

This code is for a MakeHarvard project that turns your backpack into a *third eye* for increased awareness of surroundings and safety. This is achieved with an XBox Kinect sensor and a notification bracelet that work together to enhance your senses both in the dark and light. Full documentation of this project can be found at the following link:
(will insert link when available)

There are a few steps required to enable this code to run:
- 1. Install the freenect package onto your computer from here: https://github.com/OpenKinect/libfreenect (instructions are detailed in the README file). Make sure to install the Python3 wrappers as this enables the Python code in this repository to interface with the kinect.
- 2. Install the latest version of OpenCV
- 3. Clone the repository: https://github.com/NVIDIA-AI-IOT/tf_trt_models into the root directory of this repository. Follow the instructions on the repository's README file to install the necessary dependencies and datasets. You can choose which model that the tensorflow will reference, but the default setting is defined by the variable MODEL in testing_kinect_with_tf.py as 'ssd_mobilenet_v1_coco'. Move testing_kinect_with_tf.py into the tf_trt_models folder.

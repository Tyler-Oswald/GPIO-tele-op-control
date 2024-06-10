# DeepPicar

DeepPicar is a low-cost autonomous RC car platform using a deep
convolutional neural network (CNN). DeepPicar is a small-scale replication
of [NVIDIA's real self-driving car called DAVE-2](https://developer.nvidia.com/blog/deep-learning-self-driving-cars/), which drove on public
roads using a CNN. DeepPicar uses the same CNN architecture as NVIDIA's
DAVE-2 and can drive an AWS DeepRacer in real-time without needing GPU.

## Setup

    $ git clone https://github.com/ahmedius2/DeepPicar-DeepRacer.git
    $ cd DeepPicar-DeepRacer
    $ sudo pip3 install -r requirements.txt

## Calibrate
Put the car in a position where the tires do not touch the floor and run the calibration:

    $ sudo python3 actuator-servo-deepracer.py
    
This will overwrite the pwm_calibration.json file with the new values you calibrated.

## Manual control and Data collection

    $ sudo python3 deeppicar.py -g

The gamepad (Logitech F710) commands for controlling the DeepRacer are as follows:
* **'Left Joystick'**: turn left/right
* **'Right Joystick'**: accelerate / reverse
* **'Dpad'**: discrete left/right/forward. down button toggles stop/reverse
* **'Blue 'X''**: stop the car and switch to manual mode
* **'Red 'B''**: toggle recording
* **'Green 'A''**: press once to connect
* **'Start button'**: toggle autonomous driving
* **'Back button'**: quit

The keyboard can be used instead of a gamepad by omitting the -g flag when running the deeppicar.py script. The key commands for controlling the DeepRacer are as follows:
* **'a'**: move forward 
* **'z'**: move backward
* **'s'**: stop
* **'j'**: turn left
* **'l'**: turn right 
* **'k'**: center
* **'r'**: toggle recording
* **'d'**: toggle autonomous driving
* **'q'**: quit


Use the keys or a gamepad to manually control the car. Once you become confident in controlling the car, collect the data for training the DNN model. 

The data collection can be enabled and stopped by pressing `r` key or red 'B' button on gamepad. Once recording is enabled, the video feed and the corresponding control inputs are stored in `out-video.avi` and `out-key.csv` files, respectively. Later, we will use these files for training. The car stops recording automatically when 900 frames are recorded.

If recording more than one time, rename recorded avi and csv files to out-video-XX.avi and out-key-XX.csv where XX with appropriate numbers.

Compress all the recorded files into a single zip file, say Dataset.zip. 

    $ zip Dataset.zip dataset/out-*

 Copy the file to the host PC (run this on the host PC):
 
    $ scp deepracer@<your_cars_ip_addr>:/home/deepracer/DeepPicar-DeepRacer/Dataset.zip .


## Train the model
    
Open the colab notebook. Following the notebook, you will upload the dataset to the colab, train the model, and download the model to your PC. 

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ahmedius2/DeepPicar-DeepRacer/blob/main/RunAll.ipynb)

After you are done training, you need to copy the trained tflite model file (`large-200x66x3.tflite` by default) to the DeepRacer as follows (run this on the host PC): 
    
    $ scp ~/Downloads/large-200x66x3.tflite deepracer@<your_cars_ip_addr>:/home/deepracer/DeepPicar-DeepRacer/models

## Autonomous control

Copy the trained model to the deepracer. 

Enable autonomous driving by suppling `-d` command line argument as below. 

    $ sudo python3 deeppicar.py -d 

You can also start/stop autonomous driving by pressing `d` key or Start button while running the program. 
Note that you still need to initiate a forward movement by pressing `a` or Dpad up because the DNN only controls steering.  

## Driving Videos

[![DeepPicar Driving](http://img.youtube.com/vi/SrS5iQV2Pfo/0.jpg)](http://www.youtube.com/watch?v=SrS5iQV2Pfo "DeepPicar_Video")

Some other examples of the DeepPicar driving can be found at: https://photos.app.goo.gl/q40QFieD5iI9yXU42

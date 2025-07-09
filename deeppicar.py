#!/usr/bin/python
import math
import numpy as np
import params
import argparse
import input_stream

##########################################################
# import deeppicar's sensor/actuator modules
##########################################################
actuator_servo = __import__(params.actuator)
angle = 0.0

##########################################################
# local functions
##########################################################
def deg2rad(deg):
    return deg * math.pi / 180.0
def rad2deg(rad):
    return 180.0 * rad / math.pi

##########################################################
# program begins
##########################################################

parser = argparse.ArgumentParser(description='DeepPicar main')
parser.add_argument("-t", "--throttle", help="throttle percent. [0-100]%", type=int, default=50)
parser.add_argument("-n", "--ncpu", help="number of cores to use.", type=int, default=2)
parser.add_argument("-f", "--hz", help="control frequnecy", type=int)
parser.add_argument("-g", "--gamepad", help="Use gamepad", action="store_true")
args = parser.parse_args()

if args.throttle:
    print ("throttle = %d pct" % (args.throttle))


if args.gamepad:
    cur_inp_type= input_stream.input_type.GAMEPAD
else:
    cur_inp_type= input_stream.input_type.KEYBOARD

cur_inp_stream= input_stream.instantiate_inp_stream(cur_inp_type, args.throttle)




# initlaize deeppicar modules
actuator = actuator_servo.DeepracerServo(args.throttle)

# enter main loop
while True:

    command, direction, speed = cur_inp_stream.read_inp()

    if command == 'a':
        start_ts = ts
        print (f"accel, speed: {speed}%")
    elif command == 's':
        print ("stop, time since started moving: %.2f" % (ts - start_ts))
        enable_record = False # stop recording as well 
        args.dnn = False # manual mode
    elif command == 'z':
        print (f"reverse, speed: {speed}%")
    elif command == 'y':
        actuator.shift_lims_left()
    elif command == 'h':
        actuator.shift_lims_right()
    elif command == 'q':
        actuator.stop()
        break

    actuator.set_steering(direction * 30)
    angle = deg2rad(direction * 30)
    actuator.set_throttle(speed)

print ("Finish..")

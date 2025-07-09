#!/usr/bin/python
import math
import numpy as np
import params
import argparse
import input_stream

from pi_gpio_controller import PiServoController

# Constants — adjust these to match your setup
STEERING_LEFT = 900
STEERING_CENTER = 1450
STEERING_RIGHT = 2000

THROTTLE_MIN = 1360
THROTTLE_MAX = 1536
THROTTLE_STOP = 1468  # Neutral (idle)

# Convert input [-1.0, 1.0] to PWM µs range
def scale(val, in_min, in_max, out_min, out_max):
    return int((val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

##########################################################
# Program begins
##########################################################
parser = argparse.ArgumentParser(description='Simple GPIO control')
parser.add_argument("-t", "--throttle", help="default throttle percent [0-100]", type=int, default=50)
parser.add_argument("-g", "--gamepad", help="Use gamepad", action="store_true")
args = parser.parse_args()

print(f"Throttle = {args.throttle}%")

#if args.gamepad:
cur_inp_type= input_stream.input_type.GAMEPAD
#else:
    #cur_inp_type= input_stream.input_type.KEYBOARD

cur_inp_stream= input_stream.instantiate_inp_stream(cur_inp_type, args.throttle)

actuator = PiServoController()
angle = 0.0

try:
    while True:
        command, direction, speed = cur_inp_stream.read_inp()
        print(f"Angle: {direction}  Speed: {speed}")

        # Steering: direction [-1.0, +1.0]
        steering_pwm = scale(direction, -1.0, 1.0, STEERING_LEFT, STEERING_RIGHT)
        actuator.set_steering_us(steering_pwm)

        # Throttle: speed [-100, +100]
        if speed == 0:
            throttle_pwm = THROTTLE_STOP
        elif speed > 0:
            throttle_pwm = scale(speed, 0, 100, THROTTLE_STOP, THROTTLE_MAX)
        else:
            throttle_pwm = scale(speed, -100, 0, THROTTLE_MIN, THROTTLE_STOP)

        actuator.set_throttle_us(throttle_pwm)

        if command == 'q':
            print("Stopping...")
            actuator.stop()
            break

except KeyboardInterrupt:
    actuator.stop()

print("Done.")

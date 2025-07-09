#!/usr/bin/python3
import input_stream
from pi_gpio_controller import PiServoController

def deadzone(val, deadzone=0.1):
    if abs(val) < deadzone:
        return 0.0
    if val > 0:
        return (val - deadzone) / (1 - deadzone)
    else:
        return (val + deadzone) / (1 - deadzone)
    
def throttle_deadzone(val, deadzone=10):
    if abs(val) < deadzone:
        return 0.0
    return val




#Servo PWM values
USER_SPEED_LIMIT = 40

STEERING_LEFT = 1060
STEERING_CENTER = 1600
STEERING_RIGHT = 1900


#ESC PWM values

THROTTLE_NEG_MIN = 1300 #Max reverse 
THROTTLE_NEG_MAX = 1396 #Minium throttle for reverse

THROTTLE_STOP = 1500   #Neutral

THROTTLE_POS_MIN = 1520 #Min foward 
THROTTLE_MAX = 1700   #Max foward 

#Linear scaling function for mapping the inputs to outputs 
def scale(val, in_min, in_max, out_min, out_max):
    return int((val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

#Initilze the gamepad
input_type = input_stream.input_type.GAMEPAD
inp = input_stream.instantiate_inp_stream(input_type, 0)

actuator = PiServoController()


try:
    while True:
        #Get values from the joystick
        command, direction,speed = inp.read_inp()
        #Set deadzone to avoid sticky joystick
        speed = throttle_deadzone(speed, 15)
        #Enforce a speed cap
        if speed > USER_SPEED_LIMIT:
            speed = USER_SPEED_LIMIT
        if speed < 0 and speed > -56:
            speed = -56



        #Steering PWM
        direction = deadzone(direction, .15)
        steering_pwm = scale(direction, 1.0, -1.0, STEERING_LEFT, STEERING_RIGHT)
        #Send the servo PWM to the controller
        actuator.set_steering_us(steering_pwm)

        #Throttle PWM
        #Forward
        if speed > 0:
            throttle_pwm = scale(speed, 0, 100, THROTTLE_POS_MIN, THROTTLE_MAX)
        #Reverse
        elif speed < 0:
            throttle_pwm = scale(speed, -100, 0, THROTTLE_NEG_MIN, THROTTLE_NEG_MAX)
        #Deadzone
        else:
            throttle_pwm = THROTTLE_STOP

        actuator.set_throttle_us(throttle_pwm)

        #PWM values for tuning 
        print(f"Steering: {steering_pwm:.1f}  Speed: {throttle_pwm:.2f}")



except KeyboardInterrupt:
    print("Exiting...")

finally:
    #Set the speed to 0 before exiting
    print("Stopping ESC")
    actuator.stop()


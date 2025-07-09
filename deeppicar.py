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




# Servo PWM values
USER_SPEED_LIMIT = 25

STEERING_LEFT = 1060
STEERING_CENTER = 1600
STEERING_RIGHT = 1900


# ESC PWM values
THROTTLE_MIN = 1300     # reverse
THROTTLE_STOP = 1500   # neutral
THROTTLE_MAX = 1700   # forward Normal 1860

def scale(val, in_min, in_max, out_min, out_max):
    return int((val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

input_type = input_stream.input_type.GAMEPAD
inp = input_stream.instantiate_inp_stream(input_type, 0)

actuator = PiServoController()

try:
    while True:
        command, direction,speed = inp.read_inp()
        speed = throttle_deadzone(speed, 15)
        if speed > USER_SPEED_LIMIT:
            speed = USER_SPEED_LIMIT
        if speed < 0 and speed > -56:
            speed = -56
        #elif speed < -USER_SPEED_LIMIT - 50:
            #speed = -USER_SPEED_LIMIT - 50

        # Cap speed
        print(f"Steering: {direction:.1f}  Speed: {speed:.2f}")

        # Steering PWM
        direction = deadzone(direction, .15)
        steering_pwm = scale(direction, -1.0, 1.0, STEERING_LEFT, STEERING_RIGHT)
        actuator.set_steering_us(steering_pwm)

        # Throttle PWM
        if speed > 0:
            throttle_pwm = scale(speed, 0, 100, THROTTLE_STOP, THROTTLE_MAX)
        elif speed < 0:
            throttle_pwm = scale(speed, -100, 0, THROTTLE_MIN, THROTTLE_STOP)
        else:
            throttle_pwm = THROTTLE_STOP

        actuator.set_throttle_us(throttle_pwm)

        if command == 'q':
            break

except KeyboardInterrupt:
    print("Exiting...")

finally:
    print("Stopping ESC")
    actuator.stop()


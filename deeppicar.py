#!/usr/bin/python3
import input_stream
from pi_gpio_controller import PiServoController



# Servo PWM values
USER_SPEED_LIMIT = 25

STEERING_LEFT = 1060
STEERING_CENTER = 1500
STEERING_RIGHT = 1670


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
        command, direction, speed = inp.read_inp()
        if speed > 2 and speed < 11:
            speed = 11
        elif speed > USER_SPEED_LIMIT:
            speed = USER_SPEED_LIMIT
        elif speed < -15 and speed > -30:
            speed = -25
        elif speed < -USER_SPEED_LIMIT - 25:
            speed = -USER_SPEED_LIMIT - 25

        # Cap speed
        print(f"Steering: {direction:.2f}  Speed: {speed:.1f}")

        # Steering PWM
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
            print("Exiting via 'q'")
            break

except KeyboardInterrupt:
    print("Interrupted with Ctrl+C")

finally:
    print("Stopping ESC and servo...")
    actuator.stop()


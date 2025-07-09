# pi_gpio_controller.py
import pigpio
import atexit
import time

# GPIO pins
THROTTLE_PIN = 18  # ESC
STEERING_PIN = 19  # Servo

class PiServoController:
    def __init__(self):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise Exception("Could not connect to pigpiod. Start it with 'sudo pigpiod'.")

        # Throttle range (for ESC)
        self.THROTTLE_MIN = 1060     # reverse
        self.THROTTLE_STOP = 1060    # neutral
        self.THROTTLE_MAX = 1500    # forward 



        # Steering range
        self.STEERING_LEFT = 1230
        self.STEERING_CENTER = 1390
        self.STEERING_RIGHT = 1670

        atexit.register(self.cleanup)

    def set_throttle_us(self, pwm_us):
        pwm = max(self.THROTTLE_MIN, min(self.THROTTLE_MAX, pwm_us))
        self.pi.set_servo_pulsewidth(THROTTLE_PIN, pwm)

    def set_steering_us(self, pwm_us):
        pwm = max(500, min(2500, pwm_us))
        self.pi.set_servo_pulsewidth(STEERING_PIN, pwm)

    def stop(self):
        self.set_throttle_us(self.THROTTLE_MIN)  # send neutral throttle pulse continuously
        self.set_steering_us(self.STEERING_CENTER)

    def cleanup(self):
        self.stop()
        self.pi.stop()

    def arm(self):
        # Send neutral signal to arm ESC
        self.set_throttle_us(self.THROTTLE_STOP)
        time.sleep(2)


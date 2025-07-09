import pigpio
import atexit

# GPIO pins
THROTTLE_PIN = 18  # ESC
STEERING_PIN = 19  # Servo

class PiServoController:
    def __init__(self):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise Exception("Could not connect to pigpiod. Start it with 'sudo pigpiod'.")

        # Hardcoded known good limits (you can edit these)
        self.THROTTLE_MIN = 1360
        self.THROTTLE_MAX = 1536
        self.STEERING_LEFT = 1230
        self.STEERING_CENTER = 1390
        self.STEERING_RIGHT = 1670

        atexit.register(self.cleanup)

    def set_throttle_us(self, pwm_us):
        pwm = max(500, min(2500, pwm_us))
        self.pi.set_servo_pulsewidth(THROTTLE_PIN, pwm)

    def set_steering_us(self, pwm_us):
        pwm = max(500, min(2500, pwm_us))
        self.pi.set_servo_pulsewidth(STEERING_PIN, pwm)

    def stop(self):
        self.pi.set_servo_pulsewidth(THROTTLE_PIN, 0)
        self.pi.set_servo_pulsewidth(STEERING_PIN, 0)

    def cleanup(self):
        self.stop()
        self.pi.stop()

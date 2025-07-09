# pi_gpio_controller.py
import pigpio
import atexit

#GPIO pins
THROTTLE_PIN = 18  # ESC
STEERING_PIN = 19  # Servo

class PiServoController:
    def __init__(self):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise Exception("Start pigpiod with: sudo pigpiod ")

        #Maximums for PWM throttle signals
        self.THROTTLE_MIN = 1000   # reverse
        self.THROTTLE_STOP = 1500    # neutral
        self.THROTTLE_MAX = 1900   # forward 



        #Maximus for PWM stearing signals 
        self.STEERING_LEFT = 1230
        self.STEERING_CENTER = 1390
        self.STEERING_RIGHT = 1670

        atexit.register(self.stop)
    
    def set_throttle_us(self, pwm_us):
        pwm = max(self.THROTTLE_MIN, min(self.THROTTLE_MAX, pwm_us))
        self.pi.set_servo_pulsewidth(THROTTLE_PIN, pwm)

    def set_steering_us(self, pwm_us):
        pwm = max(500, min(2500, pwm_us))
        self.pi.set_servo_pulsewidth(STEERING_PIN, pwm)

    def stop(self):
        self.set_throttle_us(self.THROTTLE_STOP) 
        self.set_steering_us(self.STEERING_CENTER)





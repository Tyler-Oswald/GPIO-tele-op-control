import pigpio
import time
import json
import atexit

PWM_CALIB_FILE = "pwm_calibration.json"

# Use GPIO 18 and 19 for hardware PWM (or any if pigpiod is running)
THROTTLE_PIN = 18  # GPIO18
STEERING_PIN = 19  # GPIO19

class PiServoController:
    def __init__(self, default_speed=0, calib_mode=False):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise Exception("Could not connect to pigpiod. Make sure it's running with 'sudo pigpiod'.")

        # Defaults (us)
        self.thr_lims = [1360, 1468, 1468, 1536]
        self.srv_lims = [1230, 1390, 1390, 1670]
        self.thr_polarity = 1
        self.srv_polarity = 1

        self.calib_mode = calib_mode
        self.read_calib_file()
        atexit.register(self.cleanup)

    def read_calib_file(self):
        try:
            with open(PWM_CALIB_FILE, 'r') as f:
                calib = json.load(f)
            self.thr_lims = calib['throttle_limits']
            self.srv_lims = calib['steering_limits']
            self.thr_polarity = calib['throttle_polarity']
            self.srv_polarity = calib['steering_polarity']
        except:
            print('Could not read calibration file, using default values.')

    def save_calib_file(self):
        with open(PWM_CALIB_FILE, 'w') as f:
            calib = {
                'throttle_limits': self.thr_lims,
                'steering_limits': self.srv_lims,
                'throttle_polarity': self.thr_polarity,
                'steering_polarity': self.srv_polarity,
            }
            json.dump(calib, f)

    def get_pwm_thr(self, pct):
        limits = self.thr_lims
        if self.thr_polarity == 1:
            if pct > 0:
                pwm = limits[2] + pct * (limits[3] - limits[2]) / 100
            elif pct < 0:
                pwm = limits[1] + pct * (limits[1] - limits[0]) / 100
            else:
                pwm = (limits[0] + limits[3]) / 2
        else:
            if pct > 0:
                pwm = limits[1] + pct * (limits[0] - limits[1]) / 100
            elif pct < 0:
                pwm = limits[2] + pct * (limits[2] - limits[3]) / 100
            else:
                pwm = (limits[0] + limits[3]) / 2
        return int(pwm)

    def get_pwm_srv(self, pct):
        limits = self.srv_lims
        if self.srv_polarity == 1:
            pct = -pct

        if pct == 0:
            pwm = (limits[1] + limits[2]) / 2
        elif pct > 0:
            pwm = limits[2] + (limits[3] - limits[2]) * pct / 100
        elif pct < 0:
            pwm = limits[1] + (limits[1] - limits[0]) * pct / 100
        return int(pwm)

    def set_throttle(self, throttle_pct):
        pct = max(-100, min(100, throttle_pct))
        pwm = self.get_pwm_thr(pct)
        self.pi.set_servo_pulsewidth(THROTTLE_PIN, pwm)

    def set_steering(self, steering_deg):
        deg = max(-30, min(30, steering_deg))
        pct = deg / 30 * 100
        pwm = self.get_pwm_srv(pct)
        self.pi.set_servo_pulsewidth(STEERING_PIN, pwm)

    def stop(self):
        self.pi.set_servo_pulsewidth(THROTTLE_PIN, 0)
        self.pi.set_servo_pulsewidth(STEERING_PIN, 0)

    def cleanup(self):
        self.stop()
        self.pi.stop()
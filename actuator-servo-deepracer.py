import os
import json
import sys
import params
import atexit

def write_to_file(path, val):
    with open(path, 'w') as f:
        f.write(val)

class DeepracerServo():
    GPIO_DIR = "/sys/class/gpio"
    PWM_DIR = "/sys/class/pwm/pwmchip0"
    PWM_PERIOD = "20000000"
    PWM_CALIB_FILE = "pwm_calibration.json"

    def __init__(self, default_speed=0, calib_mode=False):
        # read the calibration file
        # The default values below will be overwritten
        # with the values in calibration file
        self.thr_lims = [1360500, 1468500, 1468500, 1536000]
        self.srv_lims = [1230000, 1390000, 1390000, 1670000]
        self.thr_polarity = 1
        self.srv_polarity = 1
        self.inputdev = __import__(params.inputdev)

        self.calib_mode = calib_mode

        self.read_calib_file()
        print('Throttle pwm limits:', self.thr_lims)
        print('Steering pwm limits:', self.srv_lims)
        print('Polarities:', self.thr_polarity, self.srv_polarity)

        if not os.path.exists(DeepracerServo.GPIO_DIR + "/gpio436"):
            try:
                write_to_file(DeepracerServo.GPIO_DIR + "/export", "436")
            except OSError as e:
                print(f"Failed to export gpio436")
        gpio436_path = DeepracerServo.GPIO_DIR + "/gpio436"
        try:
            write_to_file(gpio436_path + "/direction", "out")
            write_to_file(gpio436_path + "/value", "0")
        except OSError as e:
            print(f"Failed to configure gpio436")

        # throttle and steering
        for pwm in ("/pwm0", "/pwm1"):
            if not os.path.exists(DeepracerServo.PWM_DIR + pwm):
                try:
                    write_to_file(DeepracerServo.PWM_DIR + "/export", pwm[-1])
                except OSError as e:
                    print(f"Failed to export {pwm}")

            try:
                write_to_file(DeepracerServo.PWM_DIR + pwm + "/period", DeepracerServo.PWM_PERIOD)
                # Disable it first to set the polarity
                # The direction of steering is determined by
                # the pwm value, not the polarity.
                write_to_file(DeepracerServo.PWM_DIR + pwm + "/enable", "0")
                write_to_file(DeepracerServo.PWM_DIR + pwm + "/polarity", "normal")
                write_to_file(DeepracerServo.PWM_DIR + pwm + "/enable", "1")
                self.stop()
            except OSError as e:
                print(f"Failed to configure {pwm}")
        atexit.register(self.cleanup)

    def cleanup(self):
        self.save_calib_file()

    def read_calib_file(self):
        try:
            with open(DeepracerServo.PWM_CALIB_FILE, 'r') as f:
                calib = json.load(f)
            self.thr_lims = calib['throttle_limits']
            self.srv_lims = calib['steering_limits']
            self.thr_polarity = calib['throttle_polarity']
            self.srv_polarity = calib['steering_polarity']

        except:
            print('Could not read calibration file, using default values.')

    def save_calib_file(self):
        with open(DeepracerServo.PWM_CALIB_FILE, 'w') as f:
            calib = {
                'throttle_limits' : self.thr_lims,
                'steering_limits' :  self.srv_lims,
                'throttle_polarity' : self.thr_polarity,
                'steering_polarity' : self.srv_polarity,
            }
            json.dump(calib, f)

    def get_pwm_thr(self, pct):
        limits = self.thr_lims
        if self.thr_polarity == 1:
            if pct > 0:
                limdiff = limits[3]-limits[2]
                pwm = limits[2] + (pct * limdiff / 100)
            elif pct < 0:
                limdiff = limits[1]-limits[0]
                pwm = limits[1] + (pct * limdiff / 100)
            else:
                pwm = limits[0] + (limits[3]-limits[0]) / 2
        else:
            if pct > 0:
                limdiff = limits[0]-limits[1]
                pwm = limits[1] + (pct * limdiff / 100)
            elif pct < 0:
                limdiff = limits[2]-limits[3]
                pwm = limits[2] + (pct * limdiff / 100)
            else:
                pwm = limits[0] + (limits[3]-limits[0]) / 2

        return int(pwm)

    # throttle_pct:v [-100, +100]
    def set_throttle(self, throttle_pct):
        # Ensure throttle_pwm is within the acceptable range
        p = max(-100, min(100, throttle_pct))
        pwm = self.get_pwm_thr(p)
        #print(f"throttle_pct: {throttle_pct} throttle_pwm: {pwm}")

        try:
            write_to_file(DeepracerServo.PWM_DIR + '/pwm0/duty_cycle', str(pwm))
        except OSError as e:
            print(f"Failed to set throttle: {e}")

    def get_pwm_srv(self, pct):
        limits = self.srv_lims
        if self.srv_polarity == 1:
            pct = -pct

        if pct == 0:
            pwm = (limits[1] + limits[2]) / 2
        elif pct>0:
            pwm = limits[2] + (limits[3] - limits[2]) * pct / 100
        elif pct<0:
            pwm = limits[1]+ (limits[1] - limits[0]) * pct / 100
        return int(pwm)

    # steering_deg: [-30, +30]
    def set_steering(self, steering_deg):
        # Ensure input is within the acceptable range
        p = max(-30, min(30, steering_deg))
        p = p / 30 * 100
        pwm = self.get_pwm_srv(p)
        #print(f"steering_deg: {steering_deg} steering_pwm: {pwm}")

        try:
            write_to_file(DeepracerServo.PWM_DIR + '/pwm1/duty_cycle', str(pwm))
        except OSError as e:
            print(f"Failed to set steering: {e}")

    def ffw(self, throttle):
        self.set_throttle(throttle)

    def stop(self):
        self.set_throttle(0)

    def drive_calib(self, init_pwm, plrty=1):
        pwm = init_pwm
        while True:
            ch = self.inputdev.read_single_event()
            if ch == ord('a'):
                pwm -= 4000 * plrty
            elif ch == ord('z'):
                pwm += 4000 * plrty
            elif ch == ord('s'): # switch polarity
                plrty *= -1
            elif ch == ord('q'):
                break

            try:
                write_to_file(DeepracerServo.PWM_DIR + '/pwm0/duty_cycle', str(pwm))
            except OSError as e:
                print(f"Failed to set throttle: {e}")

        return pwm, plrty

    def steer_calib(self, init_pwm, plrty=1):
        pwm = init_pwm
        while True:
            ch = self.inputdev.read_single_event()
            if ch == ord('a'): # increase
                pwm += 10000 * plrty
            elif ch == ord('z'): # decrease
                pwm -= 10000 * plrty
            elif ch == ord('s'): # switch polarity
                plrty *= -1
            elif ch == ord('q'):
                break
            try:
                write_to_file(DeepracerServo.PWM_DIR + '/pwm1/duty_cycle', str(pwm))
            except OSError as e:
                print(f"Failed to set steering: {e}")
        return pwm, plrty

    def do_drive_calib(self):
        print('*****************************************')
        print('Calibrating max forward throttle now.')
        print('Use A to increase the forward throttle.')
        print('Use Z to increase the backward throttle.')
        print('If the opposite is happening, press S to switch polarity.')
        print('Now adjust the throttle until desired maximum forward is reached.')
        print('Use Q button when done.')
        pwm1, p = self.drive_calib(self.thr_lims[1])
        print('\n\n*****************************************')
        print('Calibrating min forward throttle now.')
        print('Use A to increase the forward throttle.')
        print('Use Z to increase the backward throttle.')
        print('Now decrease the throttle until it stops spinning.')
        print('Then slowly increase the throttle until it starts spinning forward')
        print('Use Q button when done.')
        pwm2, p = self.drive_calib(pwm1, p)
        print('\n\n*****************************************')
        print('Calibrating max backward throttle now.')
        print('Use A to increase the forward throttle.')
        print('Use Z to increase the backward throttle.')
        print('Now adjust the throttle until desired maximum backward is reached.')
        print('Use Q button when done.')
        pwm3, p = self.drive_calib(pwm2, p)
        print('\n\n*****************************************')
        print('Calibrating min backward throttle now.')
        print('Use A to increase the forward throttle.')
        print('Use Z to increase the backward throttle.')
        print('Now decrease the throttle until it stops spinning.')
        print('Then slowly increase the throttle until it starts spinning backward')
        print('Use Q button when done.')
        pwm4, p = self.drive_calib(pwm3, p)

        self.thr_polarity = -1 if pwm1 < pwm3 else 1
        if self.thr_polarity == -1:
            self.thr_lims = [pwm1, pwm2, pwm4, pwm3]
        else:
            self.thr_lims = [pwm3, pwm4, pwm2, pwm1]

        self.save_calib_file()
        self.stop()

    def do_steering_calib(self):
        #Begin steering calibration
        print('\n\n*****************************************')
        print('Calibrating max left steering angle now.')
        print('Use A to increase the left turn angle.')
        print('Use Z to increase the right turn angle.')
        print('If the opposite is happening, press S to switch polarity.')
        print('Adjust the turning angle until the maximum left point is reached,')
        print('where increasing the angle doesnt change anything.')
        print('Use Q button when done.')
        spwm1, p = self.steer_calib(self.srv_lims[1])
        print('\n\n*****************************************')
        print('Calibrating min left steering angle now.')
        print('Use A to increase the left turn angle.')
        print('Use Z to increase the right turn angle.')
        print('Decrease the left turning angle until the tires on the right side are aligned.')
        print('Use Q button when done.')
        spwm2, p = self.steer_calib(spwm1, p)
        print('\n\n*****************************************')
        print('Calibrating max right steering angle now.')
        print('Use A to increase the left turn angle.')
        print('Use Z to increase the right turn angle.')
        print('Adjust the turning angle until the maximum right point is reached,')
        print('where increasing the angle doesnt change anything.')
        print('Use Q button when done.')
        spwm3, p = self.steer_calib(spwm2, p)
        print('\n\n*****************************************')
        print('Calibrating min right steering angle now.')
        print('Use A to increase the left turn angle.')
        print('Use Z to increase the right turn angle.')
        print('Decrease the left turning angle until the tires on the left side are aligned.')
        print('Use Q button when done.')
        spwm4, p = self.steer_calib(spwm3, p)

        self.srv_polarity = -1 if spwm1 < spwm3 else 1
        if self.srv_polarity == -1:
            self.srv_lims = [spwm1, spwm2, spwm4, spwm3]
        else:
            self.srv_lims = [spwm3, spwm4, spwm2, spwm1]

        self.save_calib_file()

    def shift_lims_left(self):
        self.thr_lims = [l  - 8000 for l in self.thr_lims]

    def shift_lims_right(self):
        self.thr_lims = [l  + 8000 for l in self.thr_lims]

if __name__ == "__main__":
    drs = DeepracerServo(0, True)

    calib = {}
    if sys.argv[1] == "calib_throttle":
        drs.do_drive_calib()
        print('\nDone!\n')
    elif sys.argv[1] == "calib_steering":
        drs.do_steering_calib()
        print('\nDone!\n')
    else:
        print('Usage 1: python3 actuator-servo-deepracer.py calib_throttle')
        print('Usage 2: python3 actuator-servo-deepracer.py calib_steering')

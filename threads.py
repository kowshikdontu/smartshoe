import time
import RPi.GPIO as GPIO
import subprocess
import threading
import board
import busio
import adafruit_vl53l0x
from adafruit_ads1x15.analog_in import AnalogIn
import Adafruit_ADS1x15


global step_cnt
# Initialize I2C bus for VL53L0X
i2c_vl53 = busio.I2C(board.SCL, board.SDA)
vl53 = adafruit_vl53l0x.VL53L0X(i2c_vl53)

i2c_adc= busio.I2C(board.SCL, board.SDA)

# Create a lock to synchronize espeak calls
espeak_lock = threading.Lock()

# Set up GPIO for Servo and Ultrasonic
SERVO_PIN = 18
TRIG = 17
ECHO = 23
step_cnt=0


def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)


def rotate_servo(angle, p):
    duty_cycle = 2.5 + (angle / 18)
    GPIO.output(SERVO_PIN, True)
    p.ChangeDutyCycle(duty_cycle)
    time.sleep(1)
    GPIO.output(SERVO_PIN, False)


def speak_text(text):
    try:
        with espeak_lock:
            subprocess.call(["espeak", text])
    except Exception as e:
        print("Error:", e)



class FSRThread(threading.Thread):


    def __init__(self, tcrt_sensor, vl53_sensor,ADC):
        threading.Thread.__init__(self)
        self.tcrt_sensor = tcrt_sensor
        self.vl53_sensor = vl53_sensor
        self.prev = False
        self.inair = False
        self.adC=ADC

    def run(self):

        while True:

            fsr_value =  self.adC.value
            if self.should_trigger(fsr_value):
                self.notify_vl53l0x()
                self.notify_tcrt5000()
            time.sleep(0.1)

    def should_trigger(self, value):
        # Implement your logic to decide when to trigger TCRT5000 and VL53L0X here
        c=0
        d=0     #remember we should specify the c and d value in class
        if c<value<d:
            return True
        else:
            return False
        pass

    def stepcounter(self,value):
        global step_cnt
        if 1000<value<1010:
            self.prev=self.inair
            self.inair=True
        else:
            self.prev=self.inair
            self.inair=False
        if self.prev ^ self.inair:
            step_cnt+=1

    def notify_vl53l0x(self):
        self.vl53_sensor.topography()
        # Implement the notification logic to VL53L0X sensor here
        pass

    def notify_tcrt5000(self):
        self.tcrt_sensor.surfacedetect()

class TCRT5000Sensor:
    def __init__(self, adc):
        self.adc = adc

    def get_value(self):
        val = self.adc.value
        return val

    def surfacedetect(self):
        n = 5
        sum = 0
        surface_ref = lambda x, y: x - 50 < y < x + 50
        # x is the l[0] or l[1].. and y is value to be checked
        ref_dict = {"oil": 234, "plain": 2356, "marble": 767, "water": 2345}
        try:
            while n:
                tcrt_value = self.get_value()  # Read the TCRT5000 value
                sum += tcrt_value
                n -= 1
                time.sleep(0.1)
                # You can convert the TCRT5000 value to distance or reflectivity as needed
            else:
                for i in ref_dict:
                    if surface_ref(ref_dict[i], sum // 5):
                        speak_text(f"flooris {ref_dict.keys[i]}")
        except  Exception as e:
            print(e)



class VL53L0XSensor:
    def __init__(self):
        self.sensor = vl53

    def notify_fsr(self):
        # Implement the notification logic to FSR here
        pass

    def topography(self):


        # Optionally, you can set the measurement mode:
        # vl53.measurement_timing_budget = 50000  # 50ms budget
        plain_ref = lambda x:  1010 < x < 1020
        n = 3
        sumv1  = 0
        while n:
            try:
                distance_mm = vl53.range
                sumv1 += distance_mm

                n -= 1
            except RuntimeError as e:
                print("Error: ", e)
        else:
            avg1 = sumv1 // 3
            if not (plain_ref(avg1)):
                comp = avg1-1000
                if comp < 0 :
                    speak_text("elevation ahead")
                if comp> 0:
                    speak_text("depression ahead")


class UltrasonicSensorThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
            pwm = GPIO.PWM(SERVO_PIN, 60)
            pwm.start(7.5)
            while True:
                    for angle in [0, 45, 90, 135, 180]:
                        rotate_servo(angle, pwm)
                        dist = self.get_distance()

                        if dist < 200:
                            speak_text(f"Obj {angle} ")

                    pwm.stop()

    def get_distance(self):
        try:
            GPIO.output(TRIG, True)
            time.sleep(0.00001)
            GPIO.output(TRIG, False)

            while GPIO.input(ECHO) == 0:
                pulse_start = time.time()

            while GPIO.input(ECHO) == 1:
                pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150
            return distance

        except KeyboardInterrupt:
            GPIO.cleanup()


def main():
    adrs=0x29
    ads = Adafruit_ADS1x15.ADS1015(i2c_adc, address=0x48)
    ads.gain=1
    fsr_channel = AnalogIn(ads, Adafruit_ADS1x15.P0)  # P0 is the channel for FSR
    tcrt_channel = AnalogIn(ads, Adafruit_ADS1x15.P1)
    vl53_sensor = VL53L0XSensor()
    tcrt_sensor = TCRT5000Sensor(tcrt_channel)
    fsr_thread = FSRThread(tcrt_sensor, vl53_sensor,fsr_channel)
    ultrasonic_thread = UltrasonicSensorThread()

    fsr_thread.start()
    ultrasonic_thread.start()


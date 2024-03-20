import time
import Adafruit_ADS1x15
import adafruit_ads1x15.ads1015 as ADS
import RPi.GPIO as GPIO
import subprocess
import board
import busio
import adafruit_vl53l0x
from adafruit_ads1x15.analog_in import AnalogIn
# Initialize I2C bus for VL53L0X
i2c_vl53 = busio.I2C(board.SCL, board.SDA)
vl53 = adafruit_vl53l0x.VL53L0X(i2c_vl53)

# Set up GPIO for Servo and Ultrasonic
SERVO_PIN = 18
TRIG = 17
ECHO = 23

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
        subprocess.call(["espeak", text])
    except Exception as e:
        print("Error:", e)


def pressureadc_value(Adrs,bno):

    # Create an ADS1015 ADC (16-bit) instance. Note you can change the I2C address from its default (0x48) and/or bus number
    adc = Adafruit_ADS1x15.ADS1015(address=Adrs, busnum=bno)
    # Choose a gain of 1 for reading voltages from 0 to 4.09V.
    GAIN = 1
    inair=prev=True
    #ref= <max pressure when crct time came>
    # Create a Loop that repeats forever
    step_cnt=0
    inAir_ref= lambda y: a<y<b
    #a,b are values of max and min we can get when shoe is in air
    vlTrig_ref=lambda y: c<y<d
    #c,d are values of max and min possible for shoe when placed forward
    while True:
        val = adc.read_adc(0, gain=GAIN)
        if inAir_ref(val):
            prev=inair
            inair=True
        else:
            prev=inair
            inair=False
        if prev ^ inair:
            step_cnt+=1
        if vlTrig_ref(val):
            #notify vl53l0x
            # notify tcrt5000


        # pause for just a tiny fraction of a second (so as not to be overwhelmed by data)
        time.sleep(0.1)



def surfaceProperty(adrs):
    # Create the I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    # Create the ADS object
    ads = ADS.ADS1015(i2c, address=adrs)  # Use the correct I2C address

    # Set the gain (if needed)
    ads.gain = 2 / 3  # This corresponds to a range of +/- 6.144V

    # Assign the analog input channel (0, 1, 2, or 3)
    chan = AnalogIn(ads, ADS.P1)  # Use the correct AIN pin
    n=5
    sum=0
    surface_ref=lambda x, y:x-50<y<x+50
    #x is the l[0] or l[1].. and y is value to be checked
    ref_dict={"oil":234,"plain":2356,"marble":767,"water":2345}
    try:
        while n:
            tcrt_value = chan.value  # Read the TCRT5000 value
            sum+=tcrt_value
            n-=1
            time.sleep(0.1)
            # You can convert the TCRT5000 value to distance or reflectivity as needed
        else:
            for i in ref_dict.keys():
                if surface_ref(ref_dict[i],sum//5):
                    speak_text(f"flooris {ref_dict.keys[i]}")

    except KeyboardInterrupt:
        pass

def sonic_distance():
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


def obstacleDetect():
        # Read the value coming from Analogue In Pin 0, set gain to the above value

        # Perform distance measurement with the ultrasonic sensor
        pwm = GPIO.PWM(SERVO_PIN, 60)
        pwm.start(7.5)

        for angle in [0, 45, 90, 135, 180]:
            rotate_servo(angle, pwm)
            dist = sonic_distance()

            if dist < 200:
                speak_text(f"Obj{angle} ")

        pwm.stop()


def topography():
    # Initialize I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    # Create a VL53L0X object
    vl53 = adafruit_vl53l0x.VL53L0X(i2c)
    vl532 = adafruit_vl53l0x.VL53L0X(i2c)

    # Optionally, you can set the measurement mode:
    # vl53.measurement_timing_budget = 50000  # 50ms budget
    plain_ref=lambda x,y: v1-e<x<v1+e and v2-e<y<v2+e
    n=3
    sumv1=sumv2=0
    while n:
        try:
            distance_mm = vl53.range
            distance_m=vl532.range
            sumv1+=distance_mm
            sumv2+=distance_m

            n-=1
        except RuntimeError as e:
            print("Error: ", e)
    else:
        avg1=sumv1/3
        avg2=sumv2/3
        if not(plain_ref(avg1,avg2)):
            comp=(avg1-v1,avg2-v2)
            if comp[0]<0 or comp[1]<0:
                speak_text("elevation ahead")
            if comp[0]>0 or comp[1]>0:
                speak_text("depression ahead")



def main():
    while True:
        GPIO.setup()
        obstacleDetect()
        pressureadc_value()


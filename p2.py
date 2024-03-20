import time
import RPi.GPIO as GPIO
import telebot
import threading
import board
import busio
import adafruit_vl53l0x
import adafruit_ads1x15.ads1015 as ADC1015
from adafruit_ads1x15.analog_in import AnalogIn
import evdev
from gps import gps, WATCH_ENABLE, WATCH_NEWSTYLE
import subprocess
from geopy.geocoders import Nominatim
import sys
from signal import signal, SIGINT

sensor_pin = 27  # Replace with the actual GPIO pin number you are using
BUZZER_PIN = 20
BUTTON_PIN = 16  # Replace with the actual GPIO pin number

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(sensor_pin, GPIO.IN)

xshut_pin_1 = 10
xshut_pin_2 = 22

GPIO.setup(xshut_pin_1, GPIO.OUT)
GPIO.output(xshut_pin_1, GPIO.HIGH)
# Initialize I2C bus for VL53L0X
i2c_vl53 = busio.I2C(board.SCL, board.SDA)
vl53 = adafruit_vl53l0x.VL53L0X(i2c_vl53, address=0x29)

i2c_adc = busio.I2C(board.SCL, board.SDA)
i2c = busio.I2C(board.SCL, board.SDA)
# Create a lock to synchronize espeak calls
espeak_lock = threading.Lock()

# Set up GPIO for Servo and Ultrasonic
SERVO_PIN = 18
TRIG = 17
ECHO = 23
step_cnt = 0

LEFT_TAP_EVENT_CODE = evdev.ecodes.KEY_PAUSECD
double_TAP_EVENT_CODE = evdev.ecodes.KEY_NEXTSONG
right_doubleTap_code = evdev.ecodes.KEY_PREVIOUSSONG

device_path = "/dev/input/event1"

device = evdev.InputDevice(device_path)

TOKEN = '6792117338:AAGWKJEU5B0iw1AO43BsxXXd3_tZmtn2z44'
CHAT_ID = [5867382409, 1844173274]  # Replace with your actual chat ID


def set_sensor_state(sensor, enable):
    sensor.shutdown = not enable
    time.sleep(0.5)  # Allow time for the sensor to stabilize


def set_gpio_state(pin, state):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, state)


def handle_sigint(signal_received, frame):
    # Cleanup GPIO and exit on Ctrl+C
    print("SIGINT or CTRL-C detected. Cleaning up and exiting gracefully.")
    GPIO.cleanup()
    sys.exit(0)


signal(SIGINT, handle_sigint)


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
    time.sleep(0.2)
    GPIO.output(SERVO_PIN, False)


def speak_text(text, voice="f1", speed=130, pitch=50):
    try:
        with espeak_lock:
            subprocess.call(["espeak", "-v", voice, "-s", str(speed), "-p", str(pitch), text])
    except Exception as e:
        print("Error:", e)


def buzz(duration=1):
    # Turn on the buzzer
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    GPIO.setwarnings(False)
    # Wait for the specified duration
    time.sleep(duration)

    # Turn off the buzzer
    GPIO.output(BUZZER_PIN, GPIO.LOW)


# Function to run the buzz function as a subprocess

class FSRThread(threading.Thread):
    def __init__(self, vl53_sensor, ADC, ultrason):
        threading.Thread.__init__(self)
        self.vl53_sensor = vl53_sensor
        self.ultrasonic = ultrason
        self.prev = False
        self.inair = False
        self.step_cnt = 0
        self.fadc = ADC
        self.fflag = True
        self.stepPrev = 0

    def run(self):
        while self.fflag:
            fsr_value = self.fadc.value
            self.stepcounter(fsr_value)
            if self.should_trigger(fsr_value):
                # self.notify_vl53l0x()
                if self.prev ^ self.inair:
                    self.notify_ultrasonic()
            time.sleep(0.1)

    def should_trigger(self, value):
        # Implement your logic to decide when to trigger TCRT5000 and VL53L0X here
        # Remember to specify the c and d values in the class
        if value > 0:
            return True
        else:
            return False

    def stop(self):
        self.fflag = False

    def stepcounter(self, value):
        global step_cnt
        if value < 0:
            self.prev = self.inair
            self.inair = True
        else:
            self.prev = self.inair
            self.inair = False
            if self.prev ^ self.inair:
                self.stepPrev = self.step_cnt
                self.step_cnt += 1
                print(self.step_cnt)

    def notify_vl53l0x(self):
        self.vl53_sensor.start()

        # Implement the notification logic to VL53L0X sensor here

    def notify_ultrasonic(self):

        self.ultrasonic.runner()


class TCRT5000Sensor(threading.Thread):
    def __init__(self, adc):
        self.adc = adc
        self.tflag = True
        super().__init__()

    def get_value(self):
        val = self.adc.value
        return val

    def stop(self):
        self.tflag = False

    def run(self):
        while self.tflag:
            surface_ref = lambda x, y: x - 50 < y < x + 50
            ref_dict = {"oil": 234, "plain": 2356, "marble": 767, "water": 2345}
            while True:
                n = 5
                sum_val = 0
                try:
                    while n:
                        tcrt_value = self.get_value()
                        sum_val += tcrt_value
                        n -= 1
                        time.sleep(0.1)
                    else:
                        for i in ref_dict:
                            if surface_ref(ref_dict[i], sum_val // 5):
                                speak_text(f"floor is {i}")
                                break
                    time.sleep(600)

                except Exception as e:
                    print(e)


class VL53L0XSensor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sensor = vl53
        self.vflag = True

    def stop(self):
        self.vflag = False

    def run(self):
        while self.vflag:
            plain_ref1 = lambda x: 100 < x < 130
            plain_ref2 = lambda y: 200 < y < 210
            n = 3
            sum_val1 = 0
            sum_val2 = 0
            ref1 = 0
            ref2 = 0
            try:
                while n:
                    # Enable and read from the first sensor
                    set_gpio_state(xshut_pin_1, GPIO.HIGH)
                    set_gpio_state(xshut_pin_2, GPIO.LOW)
                    vl53l0x_1 = adafruit_vl53l0x.VL53L0X(i2c, address=0x29)
                    set_sensor_state(vl53l0x_1, True)
                    distance_1 = vl53l0x_1.range
                    sum_val1 += distance_1
                    # Enable and read from the second sensor

                    set_gpio_state(xshut_pin_1, GPIO.LOW)
                    set_gpio_state(xshut_pin_2, GPIO.HIGH)
                    vl53l0x_1 = adafruit_vl53l0x.VL53L0X(i2c, address=0x29)
                    set_sensor_state(vl53l0x_1, True)
                    distance_2 = vl53l0x_1.range
                    sum_val2 += distance_2

                    n -= 1

                    time.sleep(0.1)
                else:
                    avg_val1 = sum_val1 // 3
                    avg_val2 = sum_val2 // 3
                    if (not plain_ref1(avg_val1)) or (not plain_ref2(avg_val2)):
                        comp1 = avg_val1 - ref1
                        comp2 = avg_val2 - ref2
                        if comp1 < 0 or comp2 < 0:
                            speak_text("elevation ahead")
                            buzz(2)
                        if comp1 > 0 or comp2 > 0:
                            speak_text("depression ahead")
                            buzz(2)
            except KeyboardInterrupt:
                set_sensor_state(vl53l0x_1, False)  # Disable the first sensor
                GPIO.cleanup()
                print("Exiting VL53L0X sensor reading.")


class UltrasonicSensorThread():
    def __init__(self):
        self.l = []
        self.uflag = True

    def stop(self):
        self.uflag = False

    def runner(self):
        pwm = GPIO.PWM(SERVO_PIN, 60)
        pwm.start(7.5)
        for angle in [0, 45, 90, 135]:
            rotate_servo(angle, pwm)
            dist = int(self.get_distance())
            if dist < 10:
                self.l.append([angle, dist])
        rotate_servo(0, pwm)
        if len(self.l) > 0:
            buzz(2)
        for i, j in self.l:
            speak_text(f"{j} meters at {i}")

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


class neo6m(threading.Thread):

    def __init__(self):
        self.al = []
        self.nflag = True
        threading.Thread.__init__(self)

    def stop(self):
        self.nflag = False

    def get_address(self, latitude, longitude):
        # Create a geolocator object using Nominatim
        geolocator = Nominatim(user_agent="geo_locator")

        # Combine latitude and longitude into a tuple
        location = (latitude, longitude)

        try:
            # Use reverse geocoding to get the address
            address = geolocator.reverse(location, language='en')
            return address.address if address else "Address not found"
        except Exception as e:
            print(f"Error: {e}")
            return "Error fetching address"

    def get_gps_coordinates(self):
        # Create a GPS object
        session = gps(mode=WATCH_ENABLE | WATCH_NEWSTYLE, device='/dev/ttyS0')

        try:
            # Stream GPS data
            session.stream(WATCH_ENABLE | WATCH_NEWSTYLE)

            while True:
                # Get data from the GPS
                report = session.next()

                # Check if GPS fix is valid
                if report['class'] == 'TPV' and hasattr(report, 'lat') and hasattr(report, 'lon'):
                    latitude = report.lat
                    longitude = report.lon
                    return latitude, longitude

        except KeyboardInterrupt:
            print("Exiting GPS data fetching.")

    def curraddress(self):
        speak_text(f"{self.get_address(self.al[2])}")

    def send_message(self):
        bot = telebot.TeleBot(TOKEN)

        message = "fuck off"
        for i in CHAT_ID:
            bot.send_message(i, message)

    def run(self):
        while self.nflag:
            la, lo = self.get_gps_coordinates()
            if len(self.al) > 3:
                self.al.pop(0)
                self.al.append((la, lo))
            else:
                self.al.append((la, lo))


class wetfloor(threading.Thread):
    def __init__(self):
        self.wflag = True
        threading.Thread.__init__(self)

    def stop(self):
        self.wflag = False

    def run(self):
        while self.wflag:
            try:
                while True:
                    sensor_value = GPIO.input(sensor_pin)
                    if sensor_value == 0:
                        speak_text("floor is wet")
                        buzz(2)
                    time.sleep(300)

            except KeyboardInterrupt:
                # Clean up GPIO on keyboard interrupt
                GPIO.cleanup()


class TWS(threading.Thread):

    def __init__(self, neo6, fsr):
        self.neo = neo6
        self.f = fsr
        self.emergency = False
        self.sflag = True
        # object of Neo6m class
        threading.Thread.__init__(self)

    def stop(self):
        self.sflag = False

    def left_tap_thread_func(self):
        speak_text(f"{self.f.step_cnt} no.of steps covered,")

    def left_doubletap_thread_func(self):

        self.neo.curraddress()

    def right_double_tap(self):
        self.emergency = not (self.emergency)
        self.neo.send_message()
        if self.emergency:
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
        else:
            GPIO.output(BUZZER_PIN, GPIO.LOW)

    def run(self) -> None:
        while self.sflag:

            for event in device.read_loop():
                if event.type == evdev.ecodes.EV_KEY:
                    if event.code == LEFT_TAP_EVENT_CODE and event.value == 1:
                        self.left_tap_thread_func()

                    elif event.code == double_TAP_EVENT_CODE and event.value == 1:
                        self.left_tap_thread_func()
                    elif event.code == right_doubleTap_code and event.value == 1:
                        self.right_double_tap()
                    else:
                        continue


GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


class ShoeController(threading.Thread):
    def __init__(self, fsr_thre, neo, raindrop, tcrt5000, tw):
        self.fsr = fsr_thre
        self.neo6m = neo
        self.rd = raindrop
        self.tcrt = tcrt5000
        self.tws = tw
        self.emergency_button_thread = None
        self.shoe_active = False
        threading.Thread.__init__(self)

    def stop(self):
        self._stop_event.set()

    def start_shoe(self):
        if not self.shoe_active:
            self.fsr.step_cnt = 0
            self.fsr.start()
            self.neo6m.start()
            self.rd.start()
            self.tws.start()
            self.tcrt.start()
            self.shoe_active = True

            speak_text("strideo assiss on")

    def stop_shoe(self):
        if not self.shoe_active:
            if self.fsr:
                self.fsr.stop()
            if self.neo6m:
                self.neo6m.stop()
            if self.rd:
                self.rd.stop()
            if self.tws:
                self.tws.stop()
            if self.tcrt:
                self.tcrt.stop()

            self.shoe_active = False
            speak_text("strideo assiss off")

    def button_press(self):

        while GPIO.input(BUTTON_PIN) == GPIO.HIGH:

            continue
        else:

            t = time.time()
            while GPIO.input(BUTTON_PIN) == GPIO.LOW:

                continue
            else:
                k = time.time()

                if k - t < 7:
                    if not self.shoe_active:
                        # Single click - Start the shoe
                        self.start_shoe()
                    else:
                        # Second click - Stop the shoe
                        self.stop_shoe()
                else:
                    # Long press - Send emergency message
                    self.neo6m.send_message()

        return True


def main():
    ads = ADC1015.ADS1015(i2c_adc, address=0x48)
    ads.gain = 1
    fsr_channel = AnalogIn(ads, ADC1015.P0)  # P0 is the channel for FSR
    tcrt_channel = AnalogIn(ads, ADC1015.P1)  # P1 is the channel for TCRT5000
    vl53_sensor = VL53L0XSensor()
    tcrt_sensor = TCRT5000Sensor(tcrt_channel)
    raindrop = wetfloor()
    neo6 = neo6m()
    ultrasonic_thread = UltrasonicSensorThread()
    fsr_thread = FSRThread(vl53_sensor, fsr_channel, ultrasonic_thread)

    t = TWS(neo6, fsr_thread)
    T = True

    shoe_controller = ShoeController(fsr_thread, neo6, raindrop, tcrt_sensor, t)
    try:
        while T:
            print("hi")
            T = shoe_controller.button_press()

    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit(0)


if __name__ == "__main__":
    setup_gpio()
    main()
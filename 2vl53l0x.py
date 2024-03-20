import RPi.GPIO as GPIO
import time
import board
import busio
import adafruit_vl53l0x

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# GPIO pins connected to XSHUT of each VL53L0X sensor
xshut_pin_1 = 10
xshut_pin_2 = 22

GPIO.setup(xshut_pin_1, GPIO.OUT)
GPIO.output(xshut_pin_1, GPIO.HIGH)


# Function to set the sensor state
def set_sensor_state(sensor, enable):
    sensor.shutdown = not enable
    time.sleep(0.5)  # Allow time for the sensor to stabilize


# Initialize I2C bus and VL53L0X sensors
i2c = busio.I2C(board.SCL, board.SDA)

# First sensor
vl53l0x_1 = adafruit_vl53l0x.VL53L0X(i2c, address=0x29)


# Second sensor
# vl53l0x_2 = adafruit_vl53l0x.VL53L0X(i2c,address=0x29)

# Function to set the GPIO state
def set_gpio_state(pin, state):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, state)


# Read and print distance measurements from each sensor
try:
    while True:
        # Enable and read from the first sensor
        set_gpio_state(xshut_pin_1, GPIO.HIGH)
        set_gpio_state(xshut_pin_2, GPIO.LOW)
        vl53l0x_1 =  adafruit_vl53l0x.VL53L0X(i2c, address=0x29)
        set_sensor_state(vl53l0x_1, True)
        distance_1 = vl53l0x_1.range
        print(f"Sensor 1: {distance_1}mm")

        # Enable and read from the second sensor

        set_gpio_state(xshut_pin_1, GPIO.LOW)
        set_gpio_state(xshut_pin_2, GPIO.HIGH)
        vl53l0x_1 = adafruit_vl53l0x.VL53L0X(i2c, address=0x29)
        set_sensor_state(vl53l0x_1, True)
        distance_2 = vl53l0x_1.range
        print(f"Sensor 2: {distance_2}mm")

        time.sleep(1)

except KeyboardInterrupt:
    set_sensor_state(vl53l0x_1, False)  # Disable the first sensor
    set_sensor_state(vl53l0x_2, False)  # Disable the second sensor
    GPIO.cleanup()
    print("Exiting VL53L0X sensor reading.")

import RPi.GPIO as GPIO
import time

# Set GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the pin connected to the TCRT5000 output
sensor_pin = 18  # Adjust based on your wiring

# Set up the sensor pin as an input
GPIO.setup(sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Read the sensor output
while True:
    sensor_value = GPIO.input(sensor_pin)
    print(f"Sensor value: {sensor_value}")
    time.sleep(0.1)
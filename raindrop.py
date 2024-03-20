import RPi.GPIO as GPIO
import time

# Set the GPIO pin
sensor_pin = 27 # Replace with the actual GPIO pin number you are using

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor_pin, GPIO.IN)

try:
    while True:
        # Read digital signal
        sensor_value = GPIO.input(sensor_pin)

        # Output the sensor value
        print(sensor_value)

        # Delay for 1 second
        time.sleep(1)

except KeyboardInterrupt:
    # Clean up GPIO on keyboard interrupt
    GPIO.cleanup()

import RPi.GPIO as GPIO
import time

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# Define the GPIO pins for the ultrasonic sensor
TRIG = 17
ECHO = 23

# Set up the GPIO pins
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

try:
    while True:
        # Trigger the ultrasonic sensor
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        # Wait for the ECHO pin to go high
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()

        # Wait for the ECHO pin to go low
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        # Calculate the duration of the pulse
        pulse_duration = pulse_end - pulse_start

        # Calculate distance in centimeters
        distance = pulse_duration * 17150

        # Print the distance
        print(f"Distance: {distance:.2f} cm")
        time.sleep(1)



except KeyboardInterrupt:
    GPIO.cleanup()

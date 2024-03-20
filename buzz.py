import RPi.GPIO as GPIO
import time
import subprocess

# Define the GPIO pin connected to the buzzer
BUZZER_PIN = 17  # Change this to the actual GPIO pin you've connected the buzzer to

# Set up GPIO mode and the buzzer pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

def buzz(duration=1):
    # Turn on the buzzer
    GPIO.output(BUZZER_PIN, GPIO.HIGH)

    # Wait for the specified duration
    time.sleep(duration)

    # Turn off the buzzer
    GPIO.output(BUZZER_PIN, GPIO.LOW)

# Function to run the buzz function as a subprocess
def run_buzz_subprocess():
    subprocess.run(["python3", "-c", "from your_module import buzz; buzz()"])

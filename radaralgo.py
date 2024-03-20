import RPi.GPIO as GPIO
import time
import subprocess

# Define GPIO pin constants
SERVO_PIN = 18
TRIG = 17
ECHO = 23

def speak_text(text):
    try:
        # Use the subprocess module to call the eSpeak command
        subprocess.call(["espeak", text])
    except Exception as e:
        print("Error:", e)

# Set up GPIO
def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)  # Disable GPIO warnings
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

# Function to rotate the servo to a specific angle
def rotate_servo(angle, p):
    duty_cycle = 2.5 + (angle / 18)
    GPIO.output(SERVO_PIN, True)
    p.ChangeDutyCycle(duty_cycle)
    time.sleep(1)
    GPIO.output(SERVO_PIN, False)

# Function to perform distance measurement with the ultrasonic sensor
def sonic_distance():
    try:
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
        return distance

    except KeyboardInterrupt:
        GPIO.cleanup()

# Main function
def main():
    try:
        setup_gpio()
        pwm = GPIO.PWM(SERVO_PIN, 50)
        pwm.start(7.5)

        for angle in [0,45, 90,135, 180]:
            rotate_servo(angle, pwm)
            dist = sonic_distance()

            if dist < 200:
                speak_text("Object is at {}".format(angle))

        pwm.stop()

    except KeyboardInterrupt:
        # Exit the script and clean up
        pwm.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()

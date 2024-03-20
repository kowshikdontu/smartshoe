import RPi.GPIO as GPIO

BUTTON_PIN = 16  # Replace with the actual GPIO pin number

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
while True:
    if GPIO.input(BUTTON_PIN) == GPIO.LOW:
        print("Button is pressed")
    else:
        print("Button is not pressed")

GPIO.cleanup()

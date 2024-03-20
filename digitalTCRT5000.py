import board
import busio
import time
import dadafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADS object
ads = ADS.ADS1015(i2c, address=0x48)  # Use the correct I2C address

# Set the gain (if needed)
ads.gain = 8 # This corresponds to a range of +/- 6.144V

# Assign the analog input channel (0, 1, 2, or 3)
chan = AnalogIn(ads, ADS.P0)  # Use the correct AIN pin

try:
    while True:
        tcrt_value = chan.value  # Read the TCRT5000 value
        print(f"TCRT5000 Value: {tcrt_value}")
        time.sleep(1)
        # You can convert the TCRT5000 value to distance or reflectivity as needed
except KeyboardInterrupt:
    pass

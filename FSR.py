#import all necessary functionality to the Script
import time
import Adafruit_ADS1x15

# Create an ADS1015 ADC (16-bit) instance. Note you can change the I2C address from its default (0x48) and/or bus number
adc = Adafruit_ADS1x15.ADS1015(address=0x48, busnum=1)
# Choose a gain of 1 for reading voltages from 0 to 4.09V.
GAIN = 1
#Create a Loop that repeats forever
while True:
    #Read the value coming from Analogue In Pin 0, set gain to the above value
    values = adc.read_adc(0, gain=GAIN)
    #Print the values to the shell, right click shell to enable the plotter
    print(values)
    #pause for just a tiny fraction of a second (so as not to be overwhelmed by data)
    time.sleep(0.1)

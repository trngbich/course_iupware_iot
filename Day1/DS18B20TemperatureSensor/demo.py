from machine import Pin
import time, ubinascii
from onewire import OneWire, DS18X20

ow = OneWire(Pin('P10'))  # create a OneWire bus on P10

temp = DS18X20(ow) # create a DS18X20 sensor object on the OneWire bus

temp.start_conversion() # send a command to the sensor to let it start the
# temperature measurement

time.sleep(1) # wait for one second (needed to ensure conversion is completed)

TempCelsius=temp.read_temp_async() # read the temperature from the sensor

print("Temperature (degrees C) = %7.1f" % TempCelsius) # print result

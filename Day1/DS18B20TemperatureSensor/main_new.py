# main.py -- put your code here!

from machine import Pin
import time, ubinascii
from onewire import OneWire, DS18X20

ow = OneWire(Pin('P10'))  # create a OneWire bus on P10

# Define function to measure the temperature with the DS18X20 sensor
# on a one-wire bus (owBUS).  If several sensors are connected to this bus
# you need to specify the ROM address of the sensor as well
# If only one DS18x20 device is attached to the bus you may omit the rom parameter.
def measureTemperature(owBus,rom=None):
    while True: # we loop until we get a valid measurement
        temp = DS18X20(owBus)
        temp.start_conversion(rom)
        time.sleep(1) # wait for one second
        TempCelsius=temp.read_temp_async(rom)
        if TempCelsius is not None:
            return TempCelsius # TempCelsius exit loop and return result

# single temperature measurement omitting the ROM parameter
SensorTempCelsius=measureTemperature(ow)
print("Temperature (degrees C) = %7.1f" % SensorTempCelsius)

# Each DS18X20 has a unique 64-bit (=8 bytes) address in its ROM memory
# (ROM = read only memory)
# When one or several DS18XB20 are connected to the same onewire bus, we can
# get their ROM addresses in the following way:
roms=ow.scan() # returns a list of bytearrays
for rom in roms: # we loop over the elements of the list
    print('ROM address of DS18XB20 = ',ubinascii.hexlify(rom))# hexlify to show
    # bytearray in hex format

# The following loop measures temperature continuously, looping over all
# sensors as well
while True: # loop forever (stop with ctrl+C)
     for rom in roms: # we loop over the elements of the list, i.e. we loop over
        # the detected DS18XB20 sensors
        print("For DS18XB20 with ROM address =", ubinascii.hexlify(rom), "the temperature (degrees C) = %7.1f" % measureTemperature(ow,rom))

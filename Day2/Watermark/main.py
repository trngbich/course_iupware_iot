# main.py = Script to read 3 Watermark sensors

import pycom, machine
from machine import Pin
import watermark # module needed in library for reading Watermark sensors (written by Jan D)

bits=12 #'Bits' can take integer values between 9 and 12 and selects the number of bits of resolution of the ADC

adc = machine.ADC(bits=bits)  # create an ADC object and specify resolution.

# Adjust vref of ADC with the value stored in NVRAM memory if available (see script in 'Calibrate ADC' script folder)
vrefmV=pycom.nvs_get('vref_mV')
if vrefmV==None : # when no value is stored
    adc.vref(1100) # new functionality in ADC, works in release '1.10.2.b1â€™ but not in older releases!
    print("ADC vref set to default value 1100 mV because no value was stored in NVRAM memory of board")
elif vrefmV<900 or vrefmV>1300 : # when value is out of range
    adc.vref(1100) # same
    print("ADC vref set to default value 1100 mV")
    print("because vrefmV from NVRAM is equal to %6.0f" % vrefmV,"mV (that is outside [900,1300])")
else :
    adc.vref(vrefmV) # same
    print("ADC vref set to %6.0f" % vrefmV,"mV (data that was stored in NVRAM of board)")

# Set up watermark sensors (each sensor requires two analog and two digital pins)
#
watermark1=watermark.watermark(adc=adc,apin1='P13',apin2='P14',dpin1=Pin('P12'),dpin2=Pin('P11'),r1ohms=6810,r2ohms=6810)
watermark2=watermark.watermark(adc=adc,apin1='P15',apin2='P16',dpin1=Pin('P10'),dpin2=Pin('P9' ),r1ohms=6810,r2ohms=6810)
watermark3=watermark.watermark(adc=adc,apin1='P17',apin2='P18',dpin1=Pin('P3' ),dpin2=Pin('P22'),r1ohms=6810,r2ohms=6810)

while True: # start endless loop
    # Read Watermark sensors
    # **********************

    soilTempCelsius=25.0 # Please replace this by a temperature measured with the DS18B20X sensor.
    # Soil temperaure is needed for temperature correrction of EC!


    wm1kohm=watermark1.read(n=10)/1000  # read 10 times to get a stable value; divide by 1000 to convert ohm >> kohm
    kPa1=watermark.ShockkPa(wm1kohm,soilTempCelsius) # calibration Shock et al. (1989)
    print("watermark 1: Resistance (kohms) = %6.3f" % wm1kohm," Water potential (kPa) = %8.2f" % kPa1)

    wm2kohm=watermark2.read(n=10)/1000
    kPa2=watermark.ShockkPa(wm2kohm,soilTempCelsius)
    print("watermark 2: Resistance (kohms) = %6.3f" % wm2kohm," Water potential (kPa) = %8.2f" % kPa2)

    wm3kohm=watermark3.read(n=10)/1000
    kPa3=watermark.ShockkPa(wm3kohm,soilTempCelsius)
    print("watermark 3: Resistance (kohms) = %6.3f" % wm3kohm," Water potential (kPa) = %8.2f" % kPa3)

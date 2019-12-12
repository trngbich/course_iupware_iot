# main.py
# Code for calibrating the ADC
# see https://docs.pycom.io/chapter/tutorials/all/adc.html

from machine import ADC
import pycom
adc=ADC()

# Step 1: output reference voltage (Vref) to an output pin (only 21 and P22 possible!)
adc.vref_to_pin('P22')

# Step 2: now measure the voltage (in mV) on that pin with an accurate multimeter

# Step 3: now save this value to NVRAM memory (SiPy1: 1120mV)
vref=1120 #  voltage (in mV) that was read with multimeter (please adapt it!)
pycom.nvs_set('vref_mV', vref) # save vref in the NVRAM memory area of the external
# flash. Data stored here is preserved across resets and power cycles.
# Value can only take 32-bit integers at the moment.

# Step 4: include the following code when starting the adc:
import pycom
vrefmV=pycom.nvs_get('vref_mV')
if vrefmV==0 :
    adc.vref(1100)
    print("ADC vref set to default value 1100 mV because no value was stored in NVRAM memory of board")
elif vrefmV<800 or vrefmV>1400 :
    adc.vref(1100)
    print("ADC vref set to default value 1100 mV")
    print("because vrefmV from NVRAM is equal to %6.0f" % vrefmV,"mV (that is outside [800,1400])")
else :
    adc.vref(vrefmV)
    print("ADC vref set to %10.0f" % vrefmV,"mV (data that was stored in NVRAM of board")

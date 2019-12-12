# main.py -- put your code here!

import machine
import pycom
import adcR # module for reading ADC and converting it to voltage

attn=3 # chose attenuation of ADC
# attn=0 (default) is 0 dB (0-1.1V) with internal reference voltage of ADC being (about) 1.1V
# attn=1 is 2.5 dB         (0-1.5V)
# attn=2 is 6 dB           (0-2.2V)
# attn=3 is 11 dB          (0-3.9V)

bits=12 #'Bits' can take integer values between 9 and 12 and selects the number
# of bits of resolution of the ADC. More bits means higher precision

adc = machine.ADC(bits=bits)  # create an ADC object and specify the resolution.

# Adjust vref of ADC with the value stored in NVRAM memory if available
# (see script 'CalibrateADC.py' in the current folder)
vrefmV=pycom.nvs_get('vref_mV')
if vrefmV==None : # when no value is stored
    adc.vref(1100) # new functionality in ADC, works in release '1.10.2.b1’ but not in older releases!
    print("ADC vref set to default value 1100 mV because no value was stored in NVRAM memory of board")
elif vrefmV<900 or vrefmV>1300 : # when value is out of range
    adc.vref(1100) # same
    print("ADC vref set to default value 1100 mV")
    print("because vrefmV from NVRAM is equal to %6.0f" % vrefmV,"mV (that is outside [900,1300])")
else :
    adc.vref(vrefmV) # same
    print("ADC vref set to %6.0f" % vrefmV,"mV (data that was stored in NVRAM of board)")

apin = adc.channel(pin='P14',attn=attn)   # Create an analog pin on P14, set attenuation.
# Valid pins are P13 to P20.
# Warning: If you are using the expansion board, then the ADC cannot be used on P19
# unless you remove jumper 'RTS'. That is because P19 on the expansion board is
# connected to FTDI_RTS. Communication through USB keeps working if jumper 'RTS' is removed.
# The ADC on P20 works fine although it is connected to FTDI_CTS. That connection
# can be cut by removing jumber 'CTS' on the expansion board

nSamples=1000 # set number of repeated measurements (to average aout the noise)
while True:
    ADCreading,Voltage=adcR.adcRead(apin,nSamples)   # read ADC and convert reading to voltage
    print("ADCreading = %6.4f" % ADCreading, "    Voltage = %8.3f" % Voltage)

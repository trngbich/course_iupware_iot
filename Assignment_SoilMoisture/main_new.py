# main.py = Script to read 3 Watermark sensors
import pycom, machine
from machine import Pin
import watermark # module needed in library for reading Watermark sensors (written by Jan D)
import time, ubinascii
from onewire import OneWire, DS18X20
from machine import RTC
from network import LoRa
import socket
import binascii
import struct
import ustruct
import config

pycom.heartbeat(False) # stop the heartbeat

# Set up the Real Time Clock (RTC)
rtc = RTC()
print(rtc.now()) # This will print date and time if it was set before going
# to deepsleep.  The RTC keeps running in deepsleep.

#WAKE UP
print("wake reason (wake_reason, gpio_list):",machine.wake_reason())
'''   PWRON_WAKE -- 0
      PIN_WAKE -- 1
      RTC_WAKE -- 2
      ULP_WAKE -- 3
 '''

for cycle in range(1):
    # initialize LoRa in LORAWAN mode.
    # Please pick the region that matches where you are using the device:
    # Asia = LoRa.AS923
    # Australia = LoRa.AU915
    # Europe = LoRa.EU868
    # United States = LoRa.US915
    lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

    # create an ABP authentication params
    dev_addr = struct.unpack(">l", binascii.unhexlify('26011752'))[0]
    nwk_swkey = binascii.unhexlify('EB0DFA7A75E6F78DC36E6E488003A811')
    app_swkey = binascii.unhexlify('04AEDDE925DA08092D91C129D3127A8B')


    # remove all the non-default channels
    for i in range(3, 16):
        lora.remove_channel(i)

    # set the 3 default channels to the same frequency
    lora.add_channel(0, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)
    lora.add_channel(1, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)
    lora.add_channel(2, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)

    # join a network using ABP (Activation By Personalization)
    lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

    # create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

    # set the LoRaWAN data rate
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, config.LORA_NODE_DR)

    # make the socket non-blocking
    s.setblocking(False)




    ow = OneWire(Pin('P21'))  # create a OneWire bus on P19
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
            print(TempCelsius)
            if TempCelsius is not None:
                return TempCelsius # TempCelsius exit loop and return result

    soilTempCelsius=measureTemperature(ow) # Please replace this by a temperature measured with the DS18B20X sensor.
    # Soil temperaure is needed for temperature correrction of EC!
    print('Soil temperature now is: %6.3f' % soilTempCelsius)


    # Read Watermark sensors
    # **********************
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


    wm1kohm=watermark1.read(n=10)/1000  # read 10 times to get a stable value; divide by 1000 to convert ohm >> kohm
    kPa1=watermark.ShockkPa(wm1kohm,soilTempCelsius) # calibration Shock et al. (1989)
    print("watermark 1: Resistance (kohms) = %6.3f" % wm1kohm," Water potential (kPa) = %8.2f" % kPa1)

    wm2kohm=watermark2.read(n=10)/1000
    kPa2=watermark.ShockkPa(wm2kohm,soilTempCelsius)
    print("watermark 2: Resistance (kohms) = %6.3f" % wm2kohm," Water potential (kPa) = %8.2f" % kPa2)

    wm3kohm=watermark3.read(n=10)/1000
    kPa3=watermark.ShockkPa(wm3kohm,soilTempCelsius)
    print("watermark 3: Resistance (kohms) = %6.3f" % wm3kohm," Water potential (kPa) = %8.2f" % kPa3)

    # create 12-bytes payload;
    # '>'=big endian;
    # 'b'=signed integer 1 byte = int:8; 'B'= unsigned integer 1 byte = uint:8;
    # 'h'=short signed integer 2 bytes = int:16 'H'=short unsigned integer 2 bytes = uint:16
    # 'i'=long signed integer 4 bytes = int:32 'I'=long unsigned integer 4 bytes = int:32
    # 'f'=float (single precision real number) 4 bytes
    # 'd'=double (double precision real number) 8 bytes

    def sendpayload(payload):
        print('Sending:', payload)
        s.send(payload)
        time.sleep(4)
        rx, port = s.recvfrom(256)
        if rx:
            print('Received: {}, on port: {}'.format(rx, port))
            stats=lora.stats()
            print(stats)
            # signal successful receipt of downlink with green led for 10 seconds
            pycom.heartbeat(False) # stop the heartbeat
            pycom.rgbled(0x007f00) # green
            time.sleep(10)
            pycom.rgbled(0) # switch led off
            pycom.heartbeat(True) # start the heartbeat
        time.sleep(6)


    payload=ustruct.pack(">fffffff",wm1kohm,kPa1,wm2kohm,kPa2,wm3kohm,kPa3,soilTempCelsius)
    sendpayload(payload)

print("Time to go to sleep ....")
sleepSeconds=5  # set deepsleep time in seconds

machine.deepsleep(sleepSeconds*1000) # time in ms

# script to send payloads to TTN through a single-channel nano-gateway
from network import LoRa
from machine import Pin
import socket
import binascii
import struct
import ustruct
import time
import config
import pycom

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

# create 12-bytes payload;
# '>'=big endian;
# 'b'=signed integer 1 byte = int:8; 'B'= unsigned integer 1 byte = uint:8;
# 'h'=short signed integer 2 bytes = int:16 'H'=short unsigned integer 2 bytes = uint:16
# 'i'=long signed integer 4 bytes = int:32 'I'=long unsigned integer 4 bytes = int:32
# 'f'=float (single precision real number) 4 bytes
# 'd'=double (double precision real number) 8 bytes
MessageNumber=0 # we need to create payload for upload but have no data
batmV=-999
hPa1=-999
hPa2=-999
hPa3=-999
soilTempCentigradeCelsius=-999
payload=ustruct.pack(">Hhhhhh",MessageNumber,batmV,hPa1,hPa2,hPa3,soilTempCentigradeCelsius)

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

# initialize `P9` in gpio mode and make it an output
led=Pin('P9', mode=Pin.OUT) # user LED on expansion board
# is connected to P9

# initialize P10 in gpio mode as input with the pull-up enabled
button=Pin('P10',mode=Pin.IN, pull=Pin.PULL_UP)# user button on
# expansion board connected to P10

def pin_handler(arg):
    print("got an interrupt in pin %s" % (arg.id()))
    led.toggle()
    sendpayload(payload)

button.callback(Pin.IRQ_RISING, pin_handler) # trigger callback function when
# button is pushed. When button is pressed, voltage on P10 falls.
# When released, it rises again and triggers callback

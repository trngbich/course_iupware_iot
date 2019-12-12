# Run this code on your Lopy4 device to get teh LoRa device EUI that you need
# to enter when registering the device on TTN
from network import LoRa
import ubinascii

lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
print("DevEUI: %s" % (ubinascii.hexlify(lora.mac()).decode('ascii')))
#70b3d54997a551c3

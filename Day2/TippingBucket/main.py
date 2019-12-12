import machine
from machine import Pin
import utime
import pycom
import micropython

micropython.alloc_emergency_exception_buf(100) # Create extra buffer to enable
# error reports to be generated from within interrupt handlers

# Initialize tip counter
nTips=0
# Initialize time of last tip (time is counted since startup)
last_interrupt_time_ms=0

# initialize `P9` in gpio mode and make it an output
led=Pin('P9', mode=Pin.OUT) # user LED on expansion board
# is connected to P9

# initialize P21 in gpio mode as input with the pull-up enabled
tippingBucket=Pin('P21',mode=Pin.IN, pull=Pin.PULL_UP)# Connect this pin
# to a switch (or reed switch in tipping bucket rain gauge) that is at the
# other side connected to ground

# Define an interrupt handler function that is called by call back
def tip_handler(arg):
    global nTips # defined as global variable so it is shared with main program
    global last_interrupt_time_ms # and preserved for subsequent pin_handler calls
    interrupt_time_ms = utime.ticks_ms()# get current time in ms since last startup
    if (interrupt_time_ms - last_interrupt_time_ms) > 500: # difference in ms
        # to avoid false tips due to switch bouncing, the time since the last 
        # valid tip needs to be sufficiently large
        led.toggle()
        nTips += 1 # increase tip counter
        print("Tip count =", nTips)
        last_interrupt_time_ms=interrupt_time_ms # preserve for next pin_handler call

tippingBucket.callback(Pin.IRQ_RISING, tip_handler) # trigger callback function when
# button is pushed. When (reed) switch closes, voltage on P21 falls.
# When released, it rises again and triggers callback

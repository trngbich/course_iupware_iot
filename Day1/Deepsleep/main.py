# main.py -- put your code here!

from machine import RTC
from machine import Pin
import pycom
import time
import machine

pycom.heartbeat(False) # stop the heartbeat

# Set up the Real Time Clock (RTC)
rtc = RTC()
print(rtc.now()) # This will print date and time if it was set before going
# to deepsleep.  The RTC keeps running in deepsleep.

# rtc.init((2019, 3, 11, 15, 39)) # manually set the time

print("wake reason (wake_reason, gpio_list):",machine.wake_reason())
'''   PWRON_WAKE -- 0
      PIN_WAKE -- 1
      RTC_WAKE -- 2
      ULP_WAKE -- 3
 '''
# blink the led
for cycles in range(2): # stop after 2 cycles
    pycom.rgbled(0x007f00) # green
    time.sleep(1)
    pycom.rgbled(0x7f7f00) # yellow
    time.sleep(1)
    pycom.rgbled(0x7f0000) # red
    time.sleep(1)
#
# # We now want to set the user button on the Expansion Board as a button
# # to wake up the lopy4 from deepsleep.  The user button on the
# # expansion board is connected to P10
# InterrupPin=Pin('P10',mode=Pin.IN, pull=Pin.PULL_UP) # define pin as input pin
# # with pull-up resistor enabled (keeps pin high as long as button is not pressed).
#
# # Now configure pin P10 as deepsleep wakeup pin.
# machine.pin_deepsleep_wakeup(pins=['P10'], mode=machine.WAKEUP_ALL_LOW, enable_pull = True)
# # With WAKEUP_ALL_LOW we ask for wakeup when the pin goes low (when button is pressed
# # the pin gets connected to ground, hence goes low)
# # With  'enable_pull = True' we keep the pull up resistor enabled during deep sleep.

print("Time to go to sleep ....")
sleepSeconds=20  # set deepsleep time in seconds

machine.deepsleep(sleepSeconds*1000) # time in ms
# Note that when it wakes from deepsleep it reboots, but the RTC keeps time during deepsleep
# You can always interrupt the deep sleep with the reset button on the LoPy4

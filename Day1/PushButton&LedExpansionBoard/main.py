from machine import Pin

# initialize `P9` in gpio mode and make it an output
led=Pin('P9', mode=Pin.OUT) # user LED on expansion board
# is connected to P9

# initialize 'P10' in gpio mode as input with the pull-up enabled
button=Pin('P10',mode=Pin.IN, pull=Pin.PULL_UP)# user button on
# expansion board is connected to P10

def pin_handler(arg): # define callback function
    print("Botton is released in pin %s" % (arg.id()))
    led.toggle()



button.callback(Pin.IRQ_RISING, pin_handler)
 # trigger callback function when
# button is pushed. When button is pressed, voltage on P10 falls.
# When released, it rises again and triggers a callback

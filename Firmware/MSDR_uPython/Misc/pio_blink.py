
'''

 This is an important intro to PIO programming

 Define the PIO blink progra using a function, then wrap it with
 the python decorator with pio configs

'''


import time
import rp2
from machine import Pin

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def blink():
    wrap_target()
    set(pins, 1) [31]  # Set pin high
    nop() [31]         # Delay
    set(pins, 0) [31]  # Set pin low
    nop() [31]         # Delay
    wrap()

# Initialize the state machine with the blink program
sm = rp2.StateMachine(0, blink, freq=20000, set_base=Pin(25))

# Run the state machine
sm.active(1)

# Run for 3 seconds
time.sleep(3)

# Stop the state machine
sm.active(0)

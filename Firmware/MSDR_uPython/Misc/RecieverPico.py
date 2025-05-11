''' Plan: 
    To communicate between two Picos: 
    To send 8 bits of data between each pico with 8 LEDs in between to illustrate whether data is being sent

    Need: How to test this?
'''

# rx.py  (run on Pico 2)
import machine

# UART0: RX=GP1
uart = machine.UART(0, baudrate=9600, tx=None, rx=machine.Pin(1))

# LED pins GP2…GP9
led_pins = [machine.Pin(i, machine.Pin.OUT) for i in range(2, 10)]

while True:
    if uart.any():
        b = uart.read(1)[0]   # get one byte
        for bit in range(8):
            led_pins[bit].value((b >> bit) & 1 == 0)  
            # value(0) will sink → LED on; value(1) → off

''' Plan: 
    To communicate between two Picos: 
    To send 8 bits of data between each pico with 8 LEDs in between to illustrate whether data is being sent

    Need: How to test this?
    Idea to test it: 

Connect the GND pins of both Pico boards together.
Connect GP0 on the transmitter Pico to GP1 on the receiver Pico.
On the receiver Pico, wire eight LEDs on GP2 through GP9, each with its anode tied to 3.3V via a 330ohm resistor and its cathode to the corresponding GPIO pin.
Save tx.py as main.py on the transmitter Pico and rx.py as main.py on the receiver Pico, then reboot both boards.
Open the serial console on the receiver Pico to verify it prints the startup banner.
Watch the LEDs cycle through the transmitted byte patterns—optionally modify tx.py to send alternating bytes 0xAA and 0x55 so you see a clear checkerboard blink.


'''
import machine, time

# UART0: TX=GP0
uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=None)

# send all bytes 0–255 in a loop
while True:
    for value in range(256):
        uart.write(bytes([value]))
        time.sleep(0.1)   # adjust to slow down or speed up

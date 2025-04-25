'''
Tie a GPIO (say GP14) high or low at boot to select “TX” vs “RX,” 
or flip TX_Mode Boolean based on software condition 

Not sure how to test this yet: could use ideas
Super basic atm 
'''
# pico_uart_led.py
import machine, time

# ——— Mode selection ———
# Option 1: compile‑time flag
TX_MODE = False  # Set True on the board you want to transmit, False on the receiver

# Option 2: hardware jumper on GP14
# mode_pin = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
# TX_MODE = mode_pin.value() == 0  # jumper closed → TX_MODE=True

#UART setup
BAUD = 9600
if TX_MODE:
    uart = machine.UART(0, BAUD, tx=machine.Pin(0), rx=None)
else:
    uart = machine.UART(0, BAUD, tx=None, rx=machine.Pin(1))

#ledsetup
led_pins = []
if not TX_MODE:
    for i in range(2, 10):
        p = machine.Pin(i, machine.Pin.OUT)
        p.value(1)   # LEDs off initially (we’re sinking to turn them on)
        led_pins.append(p)

# ——— Main loop ———
if TX_MODE:
    while True:
        for val in range(256):
            uart.write(bytes([val]))
            time.sleep(0.1)    # tune your data rate here
else:
    while True:
        if uart.any():
            b = uart.read(1)[0]
            for bit in range(8):
                # (b >> bit) & 1 == 1 → LED on, so we sink (value=0)
                led_pins[bit].value( (b >> bit) & 1 ^ 1 )

import time
import _thread
import sys
import machine

# Define the LED pin
led = machine.Pin("LED", machine.Pin.OUT)

# Function to toggle the LED and print the thread name
def task(n, delay):
    while True:  # Toggle 5 times
        led.toggle()
        sys.stdout.write(f"Thread {n} toggled LED\n")
        time.sleep(delay)

# Start two threads with different delays
_thread.start_new_thread(task, (1, 0.5))

# Main loop to blink the LED
while True:
    led.toggle()
    print("Main Loop")
    time.sleep(0.5)

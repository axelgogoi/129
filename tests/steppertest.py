import pigpio
import sys
import numpy as np
import time

# Define the motor pins.
DIR = 7
STEP = 8
ENABLE = 12

stepsPerRevolution = 3200
io = pigpio.pi()

if not io.connected:
    print("Unable to connection to pigpio daemon!")
    sys.exit(0)

io.set_mode(DIR, pigpio.OUTPUT)
io.set_mode(STEP, pigpio.OUTPUT)

io.write(ENABLE, 0)
io.write(DIR, 1)

flash_500=[]
flash_500.append(pigpio.pulse(1<<STEP, 0, 70))
flash_500.append(pigpio.pulse(0, 1<<STEP, 70))
io.wave_clear()

io.wave_add_generic(flash_500) # 500 ms flashes
f500 = io.wave_create() # create and save id

io.wave_send_repeat(f500)

time.sleep(5)

io.wave_tx_stop()
io.write(ENABLE, 1)



# for _ in range(stepsPerRevolution):
#     io.write(STEP, 1)
#     time.sleep(0.0001)
#     io.write(STEP, 0)
#     time.sleep(0.0001)
#     print("hi")

time.sleep(1)
io.write(ENABLE, 1)

import sys

sys.path.append('../129')

import time
import botutilities as bot

def printultrasonic(r):
    sensordata = r.readusensors()
    line = ""
    for sensor in sensordata:
        line = line + f"{sensor}: {sensordata[sensor]:.3f} m   "
    print(line)

def monitorultrasonic(r):
    while True:
        for usensor in r.usensors:
            usensor.pulse()
        
        printultrasonic(r)
        time.sleep(.1)

if __name__ == "__main__":

    r = bot.defaultrobot()
    
    try:
        monitorultrasonic(r)
    except BaseException as ex:
        print("Stopping due to exception: %s" % repr(ex))

    r.shutdown()

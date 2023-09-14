# Written by Axel Gogoi 
# for ME/CS/EE 129 SP '21-22
# https://github.com/axelgogoi/129

import time
import botutilities as bot
import threading
import random
from check.check_ultrasonic import *

# from check_ultrasonic import *

# states
centered = {'L': 0, 'C': 1, 'R': 0}
slightleft = {'L': 0, 'C': 1, 'R': 1}
slightright = {'L': 1, 'C': 1, 'R': 0}
alloff = {'L': 0, 'C': 0, 'R': 0}
veryleft = {'L': 0, 'C': 0, 'R': 1}
veryright = {'L': 1, 'C': 0, 'R': 0}
allon = {'L': 1, 'C': 1, 'R': 1}
inbetween = {'L': 1, 'C': 0, 'R': 1}

straightspeed = 0.2
fastturnspeed = 0.3
slowturnspeed = 0.26

scanning = False

def startscanning(r):
    global scanning
    scanning = True
    while scanning:
        for usensor in r.usensors:
            usensor.pulse()
            # print("ih")
        
        time.sleep(0.08 + 0.04 * random.random())

def stopscanning():
    global scanning
    scanning = False

def drive2obstacle(r):
    while True:
        sensordata = r.readusensors()
        printultrasonic(r)
        if sensordata['C'] > 0.2:
            r.setvel(0.3, 0)
        else:
            r.stop()

def herding(r):
    while True:
        sensordata = r.readusensors()
        # printultrasonic(r)

        case = {}
        for sensor in sensordata:
            case[sensor] = sensordata[sensor] < .2

        print(case)

        if case == alloff:
            r.setvel(straightspeed, 0)
        elif case == allon:
            r.setvel(-straightspeed, 0)
        elif case == veryleft:
            r.setvel(straightspeed, 40)
        elif case == veryright:
            r.setvel(straightspeed, -40)
        elif case == centered:
            r.setvel(-straightspeed, 30)
        elif case == inbetween:
            r.setvel(straightspeed, 0)
        elif case == slightleft:
            r.setvel(-straightspeed, -70)
        elif case == slightright:
            r.setvel(-straightspeed, 70)

def wallfollowing(r):
    d_i = 0.3
    k = 100

    while True:
        sensordata = r.readusensors()

        if sensordata['C'] < 0.2:
            r.setvel(straightspeed, -90)
        else:
            e = sensordata['L'] - d_i   
            r.setvel(straightspeed, k * e)

# 
if __name__ == "__main__":
    
    r = bot.defaultrobot()

    thread = threading.Thread(target=startscanning, args = [r])
    thread.start()
    
    try:
        # print(threading.enumerate())
        # herding(r)
        wallfollowing(r)
        
    except BaseException as ex:
        print("Stopping due to exception: %s" % repr(ex))

    stopscanning()
    thread.join()

    r.shutdown()

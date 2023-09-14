# Written by Axel Gogoi 
# for ME/CS/EE 129 SP '21-22
# https://github.com/axelgogoi/129

import botutilities as bot
import numpy as np
import time
import random

# states
centered = {'L': 0, 'C': 1, 'R': 0}
slightleft = {'L': 0, 'C': 1, 'R': 1}
slightright = {'L': 1, 'C': 1, 'R': 0}
alloff = {'L': 0, 'C': 0, 'R': 0}
veryleft = {'L': 0, 'C': 0, 'R': 1}
veryright = {'L': 1, 'C': 0, 'R': 0}
allon = {'L': 1, 'C': 1, 'R': 1}
inbetween = {'L': 1, 'C': 0, 'R': 1}

time180L = 4.77
time180R = 4.77

straightspeed = 0.6
fastturnspeed = 0.6
slowturnspeed = 0.2

turninplaceL = 90
turninplaceR = -90

WALLTHRESHOLD = 0.15
TUNNELTHRESHOLD = 0.2


def search(r):
    lost = True

    degrees = 90
    k = 0.005
    t0 = time.time()
    ds = 0

    r.setvel(0.05, 90)

    while lost:
        # r.setvel(0.4, 0) # problem 5
        istate = r.readisensors()
        if istate != alloff:
            lost = False
            print("Done searching")

        nds = int(10 * (time.time() - t0))
        if nds > ds:
            ds = nds
            degrees = 90 / (k * ds + 1)
            r.setvel(0.3, degrees)

def nodeadvance(r):
    r.go(0.3, 0, 0.7, True)

def drive(r, ultrasonic=False):
    spin = 1
    returned = False
    k = 100

    t0 = time.time()

    wallthreshold = 0
    tunnelthreshold = 0
    if ultrasonic:
        tunnelthreshold = TUNNELTHRESHOLD
        wallthreshold = WALLTHRESHOLD

    while True:
        ustate = r.readusensors()
        istate = r.readisensors()

        if ustate['L'] <= tunnelthreshold and ustate['R'] <= tunnelthreshold:
            e = ustate['L'] - ustate['R']
            r.setvelAC(0.6, k * e)

        else:
            if ustate['C'] >= wallthreshold:
                if istate == centered:
                    # when centered go straight
                    r.setvelAC(straightspeed, 0)
                elif istate == (slightleft):
                    # turn to the right slowly
                    r.setvelAC(straightspeed, -5)
                elif istate == (slightright):
                    # turn to the left slowly
                    r.setvelAC(straightspeed, 5)
                elif istate == (veryleft):
                    # turn to the right quickly
                    r.setvelAC(slowturnspeed, -30)
                elif istate == (veryright):
                    # turn to the left quickly
                    r.setvelAC(slowturnspeed, 30)
                elif istate == (inbetween):
                    # start spinning in place
                    r.setvel(fastturnspeed, 90 * spin)
                elif istate == (allon):
                    r.setvel(straightspeed, 0)
                else:
                    r.setvel(fastturnspeed, 90 * spin)
            else:
                r.go(0.3, 0, 0.3)
                turn2nextline(r, -1)
                print(ustate['C'])
                print("Turning around, obstacle in the way")
                returned = True

        if istate == allon:
            intertimer = time.time() - t0
        else:
            intertimer = 0
            t0 = time.time()

        if intertimer > 0.1:
            r.stop()
            print("Found intersection!")
            break

    if not ultrasonic:
        nodeadvance(r)
    return returned


def turn2nextline(r, d):
    '''Takes in r and d, checks distance to line and if there is none, turns
    to next line accordingly if one is detected.'''

    t0 = time.time()

    if d > 0:
        r.setvel(slowturnspeed, turninplaceL)
        time.sleep(1)
        while True:
            istate = r.readisensors()

            if istate == centered or istate == slightleft:
                r.stop()
                t = time.time() - t0
                break

        times = time180L * np.array([1 / 2, 1, 3 / 2, 2])
        idx = (np.abs(times - t)).argmin()
        output = (idx + 1)

    elif d < 0:
        r.setvel(slowturnspeed, turninplaceR)
        time.sleep(1)
        while True:
            istate = r.readisensors()

            if istate == centered or istate == slightright:
                r.stop()
                t = time.time() - t0
                break

        times = time180R * np.array([1 / 2, 1, 3 / 2, 2])
        idx = (np.abs(times - t)).argmin()
        output = -(idx + 1)

    else:
        istate = r.readisensors()
        if istate != alloff:
            output = 0
        else:
            output = None
    # print(f"Turn output: {output}")
    return output


def turn(r, m):

    global time180L
    global time180R
    global turninplaceL
    global turninplaceR

    if m == 1 or m == -3:
        r.setvel(slowturnspeed, turninplaceL)
        time.sleep(time180L / 2)
    elif m == 2:
        r.setvel(slowturnspeed, turninplaceL)
        time.sleep(time180L)
    elif m == -2:
        r.setvel(slowturnspeed, turninplaceR)
        time.sleep(time180R)
    elif m == 3 or m == -1:
        r.setvel(slowturnspeed, turninplaceR)
        time.sleep(time180R / 2)
    elif m == 0:
        r.setvel(0, 0)
    r.stop()


def calibrate(r):
    '''Takes in r, reads line until sensors
    determine the bot is centered, drives forward and course corrects
    until straight line can be travelled while tracking line until
    callibrated within satisfactory parameters.'''

    global time180L
    global time180R
    global turninplaceL
    global turninplaceR

    spin = 1
    straight = False
    t0 = time.time()
    while not straight:
        istate = r.readisensors()
        if istate == centered:
            # when centered go straight
            r.setvel(straightspeed, 0)
            if random.randint(0, 1000) == 0:
                spin = random.choice([1, -1])
        elif istate == (slightleft):
            # turn to the right slowly
            r.setvel(straightspeed, -20)
        elif istate == (slightright):
            # turn to the left slowly
            r.setvel(straightspeed, 20)
        elif istate == (veryleft):
            # turn to the right quickly
            r.setvel(fastturnspeed, -60)
        elif istate == (veryright):
            # turn to the left quickly
            r.setvel(fastturnspeed, 60)
        elif istate == (inbetween):
            # start spinning in place
            r.setvel(fastturnspeed, 90 * spin)
        elif istate == (allon):
            r.setvel(straightspeed, 0)
        else:
            r.setvel(fastturnspeed, 90 * spin)

        if istate == centered:
            straighttimer = time.time() - t0
        else:
            straighttimer = 0
            t0 = time.time()

        if straighttimer > 0.6:
            r.stop()
            straight = True
            print("Found a spot for for calibration")

    time.sleep(0.1)

    # calibrate left turns
    readingsL = []
    readingsR = []

    for _ in range(2):
        t0 = time.time()
        r.setvel(slowturnspeed, turninplaceL)
        time.sleep(1)
        istate = r.readisensors()
        while istate != centered and istate != slightleft:
            istate = r.readisensors()
        r.stop()
        readingsL.append(time.time() - t0)

        time.sleep(0.1)

    print("Done calibrating left turns")

    for _ in range(2):
        t0 = time.time()
        r.setvel(slowturnspeed, turninplaceR)
        time.sleep(1)
        istate = r.readisensors()
        while istate != centered and istate != slightright:
            istate = r.readisensors()
        r.stop()
        readingsR.append(time.time() - t0)

        time.sleep(0.1)

    time180L = np.mean(readingsL)
    time180R = np.mean(readingsR)

    print("Done calibrating right turns")
    print(f"Calibration times: {time180L} / {time180R}")


# set as standard robot
if __name__ == "__main__":

    r = bot.defaultrobot()

    try:
        calibrate(r)
        drive(r)
        turn2nextline(r, 1)
        turn2nextline(r, -1)
        drive(r)
        turn2nextline(r, -1)
        turn2nextline(r, 1)
        drive(r)
        turn2nextline(r, -1)

    except BaseException as ex:
        print("Stopping due to exception: %s" % repr(ex))

    r.shutdown()

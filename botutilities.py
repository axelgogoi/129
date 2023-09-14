# Written by Axel Gogoi 
# for ME/CS/EE 129 SP '21-22
# https://github.com/axelgogoi/129

import pigpio
import sys
import numpy as np
import time
import random

# Define the motor pins.
MTR1_DIR = 5
MTR1_STEP = 6

MTR2_DIR = 7
MTR2_STEP = 8

ENABLEPIN = 12

SENSORPINS = [14, 15, 18]

TRIGGERPINS = [13, 19, 26]
ECHOPINS = [16, 20, 21]

ACCELERATION = 1.2

DTR = 0.1

class Robot:
    def __init__(self):
        print("Setting up the GPIO...")

        io = pigpio.pi()
        self.io = io

        if not io.connected:
            print("Unable to connection to pigpio daemon!")
            sys.exit(0)

        self.steppers = []
        self.isensors = []
        self.usensors = []
        self.threads = []

    class Stepper:
        def __init__(self, io, dirpin, stppin, enblpin, k):
            self.io = io
            self.dirpin = dirpin
            self.stppin = stppin
            self.enblpin = enblpin
            self.k = k

            self.io.set_mode(dirpin, pigpio.OUTPUT)
            self.io.set_mode(stppin, pigpio.OUTPUT)
            self.io.set_mode(enblpin, pigpio.OUTPUT)

            self.speed = 0

            self.disable()

        def setspeed(self, speed):
            self.speed = speed

        def enable(self):
            self.io.write(self.enblpin, 0)

        def disable(self):
            self.io.write(self.enblpin, 1)

        def setdir(self, speed):
            if speed > 0:
                self.io.write(self.dirpin, 0)
            if speed < 0:
                self.io.write(self.dirpin, 1)

    class InfraredSensor:
        def __init__(self, io, pin, name):
            self.io = io
            self.pin = pin
            self.name = name

            self.io.set_mode(pin, pigpio.INPUT)

        def read(self):
            return self.io.read(self.pin)

        def print(self):
            print(f"{self.name}: {self.io.read(self.pin)}")

    class UltrasonicSensor:
        def __init__(self, io, triggerpin, echopin, name):
            self.io = io
            self.triggerpin = triggerpin
            self.echopin = echopin
            self.name = name

            # 0 = ready
            # 1 = waiting rising signal
            # 2 = waiting falling signal
            self.state = 0
            self.lasttick = 0
            self.lastdistance = np.inf

            self.io.set_mode(triggerpin, pigpio.OUTPUT)
            self.io.set_mode(echopin, pigpio.INPUT)

            self.cbrise = io.callback(echopin, pigpio.RISING_EDGE, self.rising)
            self.cbfall = io.callback(
                echopin, pigpio.FALLING_EDGE, self.falling)

        def pulse(self):
            if self.state == 0:
                self.io.write(self.triggerpin, 1)
                time.sleep(0.000010)
                self.io.write(self.triggerpin, 0)
                self.state = 1

        def rising(self, gpio, level, tick):
            if self.state == 1:
                self.state = 2
                self.lasttick = tick

        def falling(self, gpio, level, tick):
            if self.state == 2:
                dt = tick - self.lasttick
                if (dt < 0):
                    dt += (1 << 32)

                self.lastdistance = 0.000001 * (343 / 2) * dt
                self.state = 0

        def print(self):
            print(f"{self.name}: {self.lastdistance}")

        def read(self):
            return self.lastdistance

    def addmotor(self, dirpin, stppin, enblpin, k):
        s = self.Stepper(self.io, dirpin, stppin, enblpin, k)
        self.steppers.append(s)
        s.setspeed(0)

    def addIRsensor(self, pin, name):
        ir = self.InfraredSensor(self.io, pin, name)
        self.isensors.append(ir)

    def addUltrasonicsensor(self, triggerpin, echopin, name):
        us = self.UltrasonicSensor(self.io, triggerpin, echopin, name)
        self.usensors.append(us)

    def sendvel(self, v_l, v_r):

        if v_l != 0 and v_r != 0:
            # time units are in microseconds
            dt1 = 2 * int(1000000 * self.steppers[0].k / abs(v_l))
            dt2 = 2 * int(1000000 * self.steppers[1].k / abs(v_r))

            max_latency = 10000
            dT = np.lcm(dt1, dt2)
            if dT > max_latency:
                dT = max_latency

            toggles = []
            # motor 1
            for i in range(int(dT / dt1)):
                toggles.append((i * dt1, 0, 1))
                toggles.append((i * dt1 + int(dt1 *(1 - DTR * random.random()) / 2), 0, 0))

            # motor 2
            for i in range(int(dT / dt2)):
                toggles.append((i * dt2, 1, 1))
                toggles.append((i * dt2 + int(dt2 *(1 - DTR * random.random()) / 2), 1, 0))

            toggles.sort()
            pulses = []

            for i in range(len(toggles)):
                if (i == len(toggles) - 1):
                    if toggles[i][2]:
                        pulses.append(pigpio.pulse(
                            1 << self.steppers[toggles[i][1]].stppin, 0, dT - toggles[i][0]))
                    else:
                        pulses.append(pigpio.pulse(
                            0, 1 << self.steppers[toggles[i][1]].stppin, dT - toggles[i][0]))
                else:
                    if toggles[i][2]:
                        pulses.append(pigpio.pulse(
                            1 << self.steppers[toggles[i][1]].stppin, 0, toggles[i + 1][0] - toggles[i][0]))
                    else:
                        pulses.append(pigpio.pulse(0,
                                                   1 << self.steppers[toggles[i][1]].stppin,
                                                   toggles[i + 1][0] - toggles[i][0]))

            self.io.wave_clear()
            self.io.wave_add_generic(pulses)
            wave = self.io.wave_create()
            self.io.wave_send_repeat(wave)

    def setvel(self, v_n, theta):
        # distance between wheels is 15.25cm
        # distance from rear axle to front caster is 10.8 cm

        for s in self.steppers:
            s.enable()

        theta = theta * np.pi / 180

        v = v_n * np.cos(theta)
        omega = (1 / 0.108) * v_n * np.sin(theta)

        v_l = v - (omega * 0.1525 / 2)
        v_r = v + (omega * 0.1525 / 2)

        self.steppers[0].setdir(v_l)
        self.steppers[1].setdir(-v_r)

        v_l0 = self.steppers[0].speed
        v_r0 = self.steppers[1].speed

        self.steppers[0].speed = v_l
        self.steppers[1].speed = v_r

        if v_l0 != v_l or v_r0 != v_r:
            self.sendvel(v_l, v_r)

    def setvelAC(self, v_n, theta):

        for s in self.steppers:
            s.enable()

        theta = theta * np.pi / 180

        v = v_n * np.cos(theta)
        omega = (1 / 0.108) * v_n * np.sin(theta)

        v_l = v - (omega * 0.1525 / 2)
        v_r = v + (omega * 0.1525 / 2)

        v_l0 = self.steppers[0].speed
        v_r0 = self.steppers[1].speed

        if v_l0 != v_l or v_r0 != v_r:
            n = 50
            dvmax = max([abs(v_l - v_l0), abs(v_r - v_r0)])
            dt = dvmax / (n * ACCELERATION)

            offset = int(n / 10)

            v_l_i = np.linspace(v_l0, v_l, n)
            v_r_i = np.linspace(v_r0, v_r, n)

            for i in range(n - offset):
                self.steppers[0].setdir(v_l_i[i + offset])
                self.steppers[1].setdir(-v_r_i[i + offset])
                self.sendvel(v_l_i[i + offset], v_r_i[i + offset])
                self.steppers[0].speed = v_l_i[i + offset]
                self.steppers[1].speed = v_r_i[i + offset]
                time.sleep(dt)

    def stop(self, coast=False):
        if not coast:
            self.io.wave_tx_stop()
            time.sleep(0.1)
            for s in self.steppers:
                s.speed = 0
                s.disable()
        else:
            for s in self.steppers:
                s.speed = 0
                s.disable()
            self.io.wave_tx_stop()

    def go(self, v_n, theta, t, a = False):
        # drive at a speed for a time
        if a:
            self.setvelAC(v_n, theta)
        else:
            self.setvel(v_n, theta)
        time.sleep(t)
        self.stop()

    def beep(self):
        self.go(12, 0, 0.6)

    def readisensors(self):
        sensordata = {}
        for sensor in self.isensors:
            sensordata[sensor.name] = sensor.read()
        return sensordata

    def readusensors(self):
        sensordata = {}
        for sensor in self.usensors:
            sensordata[sensor.name] = sensor.read()
        return sensordata

    def shutdown(self):
        print("Shutting down now")
        self.stop()
        for thread in self.threads:
            thread.join()
        self.io.stop()


def defaultrobot():
    r = Robot()
    r.addmotor(MTR1_DIR, MTR1_STEP, ENABLEPIN, 0.0001)
    r.addmotor(MTR2_DIR, MTR2_STEP, ENABLEPIN, 0.0001)
    r.addIRsensor(14, "L")
    r.addIRsensor(15, "C")
    r.addIRsensor(18, "R")

    #1 is left, 2 is front, 3 is right
    r.addUltrasonicsensor(13, 16, "L")
    r.addUltrasonicsensor(19, 20, "C")
    r.addUltrasonicsensor(26, 21, "R")
    return r


if __name__ == "__main__":
    r = defaultrobot()

    print("hi")

    t0 = time.time()
    r.setvel(0.4, 45)
    time.sleep(5)
    print(time.time() - t0)

    r.shutdown()

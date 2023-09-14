import botutilities as bot
import time

centered = {'L': 0, 'C': 1, 'R': 0}
slightleft = {'L': 0, 'C': 1, 'R': 1}
slightright = {'L': 1, 'C': 1, 'R': 0}
alloff = {'L': 0, 'C': 0, 'R': 0}


veryleft = {'L': 0, 'C': 0, 'R': 1}
veryright = {'L': 1, 'C': 0, 'R': 0}
allon = {'L': 1, 'C': 1, 'R': 1}
inbetween = {'L': 1, 'C': 0, 'R': 1}

lost = True
losttimer = 0


def searchforline(r):
    global lost

    degrees = 90
    k = 0.005
    t0 = time.time()
    ds = 0

    r.setvel(0.3, 90)

    while lost:
        # r.setvel(0.4, 0) # problem 5
        state = r.readisensors()
        if state != alloff:
            lost = False

        nds = int(10 * (time.time() - t0))
        if nds > ds:
            ds = nds
            degrees = 90 / (k * ds + 1)
            r.setvel(0.3, degrees)


def followline(r):
    global lost
    laststate = {}
    spin = 1
    while not lost:
        state = r.readisensors()
        if state == centered:
            # when centered go straight
            r.setvel(0.3, 0)
        elif state == (slightleft):
            # turn to the right slowly
            r.setvel(0.35, -35)
        elif state == (slightright):
            # turn to the left slowly
            r.setvel(0.35, 35)
        elif state == (veryleft):
            # turn to the right quickly
            r.setvel(0.3, -60)
        elif state == (veryright):
            # turn to the left quickly
            r.setvel(0.3, 60)
        elif state == (allon):
            # start spinning in place
            r.setvel(0.3, 90 * spin)
        elif state == (inbetween):
            # start spinning in place
            r.setvel(0.3, 90 * spin)
        else:
            # use last state to determine if line ended or pushed off line
            if laststate == (veryleft):
                # veer hard right if pushed left
                r.setvel(0.3, -60)
            elif laststate == (veryright):
                # veer hard left if pushed right
                r.setvel(0.3, 60)
            # elif laststate == (slightleft):
            #     # turn right if righthand corner found
            #     r.setvel(0.4, -60)
            #     spin = - 1
            # elif laststate == (slightright):
            #     # veer hard left if pushed right
            #     r.setvel(0.4, 60)
            #     spin = 1
            # elif laststate == (centered) or laststate == (
            #         slightleft) or laststate == (slightright):
            #     # stop if at end of the line (only for problem 4 and 5)
            #     r.stop()
            else:
                # spin in place if none of this applies
                r.setvel(0.6, 90 * spin)
        # saves last state that contains turning information
        if state == slightleft or state == slightright or state == veryleft or state == veryright:
            laststate = state.copy()

        if state == alloff:
            losttimer = time.time() - starttime
        else:
            losttimer = 0
            starttime = time.time()

        if losttimer > 10:
            lost = True
            print("Oh no! I'm lost <ó w ò>")


# set as standard robot
if __name__ == "__main__":

    r = bot.defaultrobot()

    try:
        while True:
            searchforline(r)
            followline(r)
    except BaseException as ex:
        print("Stopping due to exception: %s" % repr(ex))

    r.shutdown()

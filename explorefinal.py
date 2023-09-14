# Written by Axel Gogoi 
# for ME/CS/EE 129 SP '21-22
# https://github.com/axelgogoi/129

import botutilities as bot
import time
import gridbehaviors as gb
import random
import numpy as np
import threading

import ultrasonic_behaviors as ub

from exploregrid import followpath
from maputilities import *
from mapmaker import *
from tkinter import *


# Global Variables:
nodelist = []
heading = NORTH
currentnode = None
previousnode = None
donemapping = False
pausemapping = False
exitflag = False

FARTHRESHOLD = 0.3
CLOSETHRESHOLD = 0.1


def completeexplore(r, x0=0, y0=0, xtarget=None, ytarget=None):

    # prepare variables
    global nodelist
    global heading
    global currentnode
    global previousnode
    global donemapping
    global pausemapping
    global exitflag

    pathed = False
    returned = False

    try:
        root = Tk()
        root.geometry(f'{xsize}x{ysize}')
        canvas = Canvas(root, width=xsize, height=ysize)
        canvas.pack()
    except BaseException as ex:
        print(ex)
        pass

    # drive to first intersection
    gb.drive(r, True)

    # start main loop
    while not donemapping:

        # consider special cases first
        if pathed:
            # robot just finished executing a path
            print("Skipping node update due to path")
            closestunexplorednode = None
        elif returned:
            # robot just returned from blocked path
            print("Returning to previous node due to obstacle")
            currentnode.blocked[heading] = True
            heading = (heading + 2) % 4
            returned = False
            currentnode = previousnode
        else:
            # update x and y coordinates
            try:
                x = previousnode.x
                y = previousnode.y

                if heading % 4 == NORTH:
                    y = y + 1
                elif heading % 4 == WEST:
                    x = x - 1
                elif heading % 4 == SOUTH:
                    y = y - 1
                elif heading % 4 == EAST:
                    x = x + 1
                else:
                    raise Exception("This can't be")
            # set x and y to zero if at first node
            except BaseException:
                x = x0
                y = y0

            # get current node if it exists, or create one if it doesn't
            if getnode(x, y, nodelist) is None:
                currentnode = Node(x, y)
            else:
                currentnode = getnode(x, y, nodelist)

        time.sleep(0.2)
        print(f"Arriving at {currentnode} with heading {heading}")

        # update visual map if in virtual desktop

        try:
            updategraph(canvas, nodelist, currentnode.xy(), heading)
            root.update()
        except BaseException:
            pass

        # pre-calculate directions
        forward = heading
        left = (heading + 1) % 4
        right = (heading - 1) % 4
        backward = (heading + 2) % 4

        # create link between current and previous node, except in certain
        # cases
        if previousnode is not None:
            # ignore if robot followed path or if coming from same node
            if not pathed and currentnode.xy() != previousnode.xy():
                try:
                    previousnode.streets[heading] = CONNECTED
                    currentnode.streets[backward] = CONNECTED
                except BaseException:
                    currentnode.streets[backward] = UNEXPLORED
        else:
            if not pathed:
                try:
                    previousnode.streets[heading] = CONNECTED
                    currentnode.streets[backward] = CONNECTED
                except BaseException:
                    currentnode.streets[backward] = UNEXPLORED
        pathed = False

        # read ultrasonic sensors everytime
        ustate = r.readusensors()
        for u, h in zip(['L', 'C', 'R'], [left, forward, right]):
            if ustate[u] < FARTHRESHOLD:
                currentnode.blocked[h] = True
            else:
                currentnode.blocked[h] = False
        intunnel = ustate['L'] <= gb.TUNNELTHRESHOLD and ustate['R'] <= gb.TUNNELTHRESHOLD

        # add unblocked streets to list of avaliable streets
        availablestreets = []
        for i in range(len(currentnode.blocked)):
            if not currentnode.blocked[i]:
                availablestreets.append(i)

        gb.nodeadvance(r)

        print(f"Blocked headings: {currentnode.blocked}")
        time.sleep(0.2)

        if UNKNOWN in currentnode.streets:
            # if current node hasn't been explored, scan intersection
            print("> New intersection found")

            if intunnel:
                currentnode.streets[left] = UNKNOWN
                currentnode.streets[right] = UNKNOWN
                currentnode.streets[forward] = UNEXPLORED

                currentnode.blocked[left] = True
                currentnode.blocked[right] = True

                print("  > Intersection is in tunnel")
                print(f"> Streets [NWSE]: {currentnode.streets}")
                print(f"> Unexplored: {unexploredstreets}")
                print(f"> Available: {availablestreets}")
            else:

                unexploredstreets = []

                # check if there's a street straight ahead
                if currentnode.streets[forward] == UNKNOWN:
                    turndata = gb.turn2nextline(r, 0)
                    if turndata == 0:
                        currentnode.streets[forward] = UNEXPLORED
                        unexploredstreets.append(forward)
                    else:
                        currentnode.streets[forward] = NOSTREET

                # check if there's a side street to the left
                # rotate the robot to face backwards anyway
                if currentnode.streets[left] == UNKNOWN:
                    turndata = gb.turn2nextline(r, 1)
                    if turndata == 1:
                        currentnode.streets[left] = UNEXPLORED
                        unexploredstreets.append(left)
                        gb.turn2nextline(r, 1)
                    elif turndata == 2:
                        currentnode.streets[left] = NOSTREET

                # check if there's a side street to the right
                # rotate the robot back to face backwards anyway
                if currentnode.streets[right] == UNKNOWN:
                    turndata = gb.turn2nextline(r, 1)
                    if turndata > 1:
                        currentnode.streets[right] = NOSTREET
                    else:
                        currentnode.streets[right] = UNEXPLORED
                        unexploredstreets.append(right)
                    if turndata == 3:
                        gb.turn2nextline(r, 1)
                    elif turndata < 3:
                        turndata = gb.turn2nextline(r, -1)

                print("  > Done scanning intersection")
                heading = (heading + 2) % 4

                preferredstreets = list(
                    set(availablestreets) & set(unexploredstreets))

                print(f"> Streets [NWSE]: {currentnode.streets}")
                print(f"> Unexplored: {unexploredstreets}")
                print(f"> Available: {availablestreets}")
                print(f"> Preferred: {preferredstreets}")

                # try to explore unexplored streets, unless its a dead end
                try:
                    if xtarget is None or ytarget is None:
                        nextstreet = random.choice(preferredstreets)
                        print("not targheting")
                    else:
                        print("targeting")
                        nextstreet = nextbeststreet(
                            x, y, xtarget, ytarget, preferredstreets)

                    turn = (nextstreet - heading + 2) % 4 - 2
                    heading = nextstreet

                    print(
                        f"Next heading: {nextstreet} / Turn direction: {turn}")

                    if abs(turn) == 1:
                        gb.turn2nextline(r, turn)

                    elif abs(turn) == 2:
                        gb.turn2nextline(r, turn / abs(turn))
                        if currentnode.streets[(
                                heading - turn + int(turn / abs(turn))) % 4] != NOSTREET:
                            gb.turn2nextline(r, turn / abs(turn))
                except BaseException as ex:
                    print(ex)
                    print(f"Next heading: {heading} / Turn direction: {0}")

            # add current node to node list
            nodelist.append(currentnode)

        else:
            if not intunnel:
                unexploredstreets = []
                for i in range(len(currentnode.streets)):
                    if currentnode.streets[i] == UNEXPLORED:
                        unexploredstreets.append(i)

                preferredstreets = list(
                    set(availablestreets) & set(unexploredstreets))

                if preferredstreets != []:
                    # if some streets are still unexplored, randomly choose
                    # from them
                    print("> Already visited, but some streets unexplored")
                    print(f"> Streets [NWSE]: {currentnode.streets}")
                    print(f"> Unexplored: {unexploredstreets}")

                    if xtarget is None or ytarget is None:
                        nextstreet = random.choice(preferredstreets)
                    else:
                        nextstreet = nextbeststreet(
                            x, y, xtarget, ytarget, preferredstreets)

                    turn = (nextstreet - heading + 2) % 4 - 2
                    heading = nextstreet

                    print(
                        f"Next heading: {nextstreet} / Turn direction: {turn}")
                    gb.turn2nextline(r, turn)

                else:
                    # if all streets are explored, randomly choose from them
                    print("> Already visited, all streets explored")
                    print(f"> Streets [NWSE]: {currentnode.streets}")
                    print(f"> Unexplored: {unexploredstreets}")

                    if xtarget is None or ytarget is None:
                        xgoal = x
                        ygoal = y
                    else:
                        xgoal = xtarget
                        ygoal = ytarget

                    closestunexplorednode = None
                    mindistance = math.inf
                    for node in nodelist:
                        if UNEXPLORED in node.streets and node.xy() != currentnode.xy():
                            xy = node.xy()

                            distance = math.sqrt(
                                (xgoal - xy[0])**2 + (ygoal - xy[1])**2)
                            if distance < mindistance and len(dijkstra(nodelist, x, y, xy[0], xy[1])) > 1:
                                mindistance = distance
                                closestunexplorednode = node

                    if xtarget is None or ytarget is None:
                        print(
                            f"> Closest Unexplored Node: {closestunexplorednode}")
                    else:
                        print(
                            f"> Closest Unexplored Node to Target: {closestunexplorednode}")

                    if closestunexplorednode is not None:
                        goalx = closestunexplorednode.x
                        goaly = closestunexplorednode.y
                        path = dijkstra(nodelist, x, y, goalx, goaly)

                        print(
                            f"Preparing to travel to Closest Unexplored Node on path {path}")

                    else:
                        print(f"No nodes with unexplored streets, randomly exploring")

                        # create list of connected streets
                        connectedstreets = []
                        for i in range(len(currentnode.streets)):
                            if currentnode.streets[i] == CONNECTED:
                                connectedstreets.append(i)

                        possiblestreets = list(
                            set(availablestreets) & set(connectedstreets))

                        # if node is not a dead end, remove the backwards
                        # direction
                        if len(possiblestreets) > 1:
                            possiblestreets.remove(backward)

                        if xtarget is None or ytarget is None:
                            nextstreet = random.choice(possiblestreets)
                        else:
                            nextstreet = nextbeststreet(
                                x, y, xtarget, ytarget, possiblestreets)
                        turn = (nextstreet - heading + 2) % 4 - 2
                        heading = nextstreet

                        print(
                            f"Next heading: {nextstreet} / Turn direction: {turn}")
                        gb.turn2nextline(r, turn)
            else:
                print("> Previously visited tunnel node, proceeding forward")

        previousnode = currentnode

        # update visual map if in virtual desktop
        try:
            updategraph(canvas, nodelist, currentnode.xy(), heading)
            root.update()
        except BaseException:
            pass

        print(f"\nNode List ({len(nodelist)} nodes): {nodelist}")
        print("------------------------------------------------")

        while pausemapping:
            pass

        if donemapping or currentnode.xy() == (xtarget, ytarget):
            if currentnode.xy() == (xtarget, ytarget):
                r.beep()
                donemapping = True
            break

        if 'closestunexplorednode' in locals() and closestunexplorednode is not None:
            time.sleep(1)
            root.destroy()
            (x, y, heading) = followpath(r, heading, path, nodelist, True)
            currentnode = getnode(x, y, nodelist)
            pathed = True

            try:
                root = Tk()
                root.geometry(f'{xsize}x{ysize}')
                canvas = Canvas(root, width=xsize, height=ysize)
                canvas.pack()
                updategraph(canvas, nodelist, currentnode.xy(), heading)
                root.update()
            except BaseException:
                pass
        else:
            returned = gb.drive(r, True)

    try:
        root.destroy()
    except:
        pass
   
    exitflag = True


def timeout_error(*_):
    raise TimeoutError


def nextbeststreet(x0, y0, xtarget, ytarget, streets):

    print(f"Current Location: ({x0}, {y0}) / Goal: ({xtarget}, {ytarget})")

    beststreet = streets[0]
    bestdistance = np.inf

    for street in streets:
        if street % 4 == NORTH:
            x = x0
            y = y0 + 1
        elif street % 4 == WEST:
            x = x0 - 1
            y = y0
        elif street % 4 == SOUTH:
            x = x0
            y = y0 - 1
        elif street % 4 == EAST:
            x = x0 + 1
            y = y0

        distance = math.sqrt((xtarget - x)**2 + (ytarget - y)**2)
        if distance < bestdistance:
            bestdistance = distance
            beststreet = street
        elif distance == bestdistance:
            beststreet = random.choice([street, beststreet])
        print(x, y, street, distance)
    return beststreet


# go from user-specified node to user-specified node
def planmode(r, nodelist, startx, starty, heading, ultrasonic=False):
    print("Entering planned driving mode")

    x = startx
    y = starty

    while True:
        try:
            root = Tk()
            root.geometry(f'{xsize}x{ysize}')
            canvas = Canvas(root, width=xsize, height=ysize)
            canvas.pack()
            updategraph(canvas, nodelist, currentnode.xy(), heading)
            root.update()
        except BaseException:
            pass

        goalx = input("Type in Desired x-coordinate (enter nothing to quit): ")
        if goalx == '':
            break
        goaly = input("Type in Desired y-coordinate (enter nothing to quit): ")
        if goaly == '':
            break
        path = dijkstra(nodelist, x, y, int(goalx), int(goaly))
        print("")

        try:
            root.destroy()
        except BaseException:
            pass

        (x, y, heading) = followpath(r, heading, path, nodelist, ultrasonic)
        print(f"\nNode List: {nodelist}")
        print("------------------------------------------------")


# set as standard robot
if __name__ == "__main__":

    # donemapping = False
    r = bot.defaultrobot()
    thread = threading.Thread(target=ub.startscanning, args=[r])
    thread.start()

    try:
        gb.search(r)
        # gb.calibrate(r)
        completeexplore(r)
        print("Done exploring")
        print(f"Current Node: {currentnode}")
        print(f"Current Heading: {heading}")

        print("------------------------------------------------")
        planmode(
            r,
            nodelist,
            currentnode.x,
            currentnode.y,
            heading,
            root,
            canvas)

    except BaseException as ex:
        print("Stopping due to exception: %s" % repr(ex))

    ub.stopscanning()
    thread.join()

    r.shutdown()

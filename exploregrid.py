# Written by Axel Gogoi 
# for ME/CS/EE 129 SP '21-22
# https://github.com/axelgogoi/129

import botutilities as bot
import time
import signal
import gridbehaviors as gb
import random
import math

from maputilities import *
from mapmaker import *
from tkinter import *


# Global Variables:
nodelist = []
heading = NORTH
currentnode = None
donemapping = False


def betterexplore(r, tkroot=None, tkcanvas=None):

    # prepare variables
    global nodelist
    global currentnode
    global heading
    global donemapping

    previousnode = None
    skip = False

    # drive to first intersection

    gb.drive(r)

    # start main loop
    while not donemapping:
        # update x and y coordinates

        if skip:
            print("Skipping")
            closestunexplorednode = None
        else:
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
                x = 0
                y = 0

            # get current node if it exists, or create one if it doesn't
            if getnode(x, y, nodelist) is None:
                currentnode = Node(x, y)
            else:
                currentnode = getnode(x, y, nodelist)

        time.sleep(0.1)
        print(f"Arriving at {currentnode} with heading {heading}")

        # update visual map if in virtual desktop
        try:
            updategraph(tkcanvas, nodelist, currentnode.xy(), heading)
            tkroot.update()
        except BaseException:
            pass

        # pre-calculate directions
        forward = heading
        left = (heading + 1) % 4
        right = (heading - 1) % 4
        backward = (heading + 2) % 4

        if not skip:
            # create link between current and previous node, unless its the
            # first node
            try:
                previousnode.streets[heading] = CONNECTED
                currentnode.streets[backward] = CONNECTED
            except BaseException:
                currentnode.streets[backward] = UNEXPLORED

        skip = False

        if UNKNOWN in currentnode.streets:
            # if current node hasn't been explored, scan intersection
            print("> New intersection found")

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

            print(f"> Streets [NWSE]: {currentnode.streets}")
            print(f"> Unexplored: {unexploredstreets}")

            # try to explore unexplored streets, unless its a dead end
            try:
                nextstreet = random.choice(unexploredstreets)
                turn = (nextstreet - heading + 2) % 4 - 2
                heading = nextstreet

                print(f"Next heading: {nextstreet} / Turn direction: {turn}")

                if abs(turn) == 1:
                    gb.turn2nextline(r, turn)

                elif abs(turn) == 2:
                    gb.turn2nextline(r, turn / abs(turn))
                    if currentnode.streets[(
                            heading - turn + int(turn / abs(turn))) % 4] != NOSTREET:
                        gb.turn2nextline(r, turn / abs(turn))
            except BaseException:
                # dead end case; unexploredstreets = []
                print(f"Next heading: {heading} / Turn direction: {0}")

            # add current node to node list
            nodelist.append(currentnode)

        else:
            # connect current node and previous node
            currentnode.streets[backward] = CONNECTED
            previousnode.streets[heading] = CONNECTED

            # create list of unexplored streets
            unexploredstreets = []
            for i in range(len(currentnode.streets)):
                if currentnode.streets[i] == UNEXPLORED:
                    unexploredstreets.append(i)

            if unexploredstreets != []:
                # if some streets are still unexplored, randomly choose from
                # them
                print("> Already visited, but some streets unexplored")
                print(f"> Streets [NWSE]: {currentnode.streets}")
                print(f"> Unexplored: {unexploredstreets}")

                nextstreet = random.choice(unexploredstreets)
                turn = (nextstreet - heading + 2) % 4 - 2
                heading = nextstreet

                print(f"Next heading: {nextstreet} / Turn direction: {turn}")
                gb.turn2nextline(r, turn)

            else:
                # if all streets are explored, randomly choose from them
                print("> Already visited, all streets explored")
                print(f"> Streets [NWSE]: {currentnode.streets}")
                print(f"> Unexplored: {unexploredstreets}")

                closestunexplorednode = None
                mindistance = math.inf
                for node in nodelist:
                    if UNEXPLORED in node.streets:
                        xy = node.xy()

                        distance = math.sqrt((x - xy[0])**2 + (y - xy[1])**2)
                        if distance < mindistance:
                            mindistance = distance
                            closestunexplorednode = node

                print(f"> Closest Unexplored Node: {closestunexplorednode}")

                if closestunexplorednode is not None:
                    goalx = closestunexplorednode.x
                    goaly = closestunexplorednode.y
                    path = dijkstra(nodelist, x, y, goalx, goaly)

                    print(
                        f"Preparing to travel to Closest Unexplored Node on path {path}")

                else:
                    print(
                        f"No nodes with unexplored streets, randomly exploring {path}")

                    # create list of connected streets
                    connectedstreets = []
                    for i in range(len(currentnode.streets)):
                        if currentnode.streets[i] == CONNECTED:
                            connectedstreets.append(i)

                    # if node is not a dead end, remove the backwards direction
                    if len(connectedstreets) > 1:
                        connectedstreets.remove(backward)

                    nextstreet = random.choice(connectedstreets)
                    turn = (nextstreet - heading + 2) % 4 - 2
                    heading = nextstreet

                    print(
                        f"Next heading: {nextstreet} / Turn direction: {turn}")
                    gb.turn2nextline(r, turn)

        previousnode = currentnode

        # update visual map if in virtual desktop
        try:
            updategraph(tkcanvas, nodelist, currentnode.xy(), heading)
            tkroot.update()
        except BaseException:
            pass

        signal.signal(signal.SIGALRM, timeout_error)
        signal.alarm(2)
        try:
            input("\nPRESS ENTER within 2 seconds to stop exploring")
            signal.alarm(0)
            donemapping = True
        except TimeoutError:
            print(" / Input timed out; continuing exploring")
            signal.signal(signal.SIGALRM, signal.SIG_IGN)

            if 'closestunexplorednode' in locals() and closestunexplorednode is not None:
                time.sleep(1)
                (x, y, heading) = followpath(
                    r, heading, path, nodelist, tkroot, tkcanvas)
                currentnode = getnode(x, y, nodelist)
                skip = True
            else:
                gb.drive(r)

        print(f"\nNode List ({len(nodelist)} nodes): {nodelist}")
        print("------------------------------------------------")


def timeout_error(*_):
    raise TimeoutError

# follow a sequence of nodes


def followpath(r, startheading, path, nodelist, ultrasonic=False):

    try:
        root = Tk()
        root.geometry(f'{xsize}x{ysize}')
        canvas = Canvas(root, width=xsize, height=ysize)
        canvas.pack()
        updategraph(canvas, nodelist, currentnode.xy(), heading)
        root.update()
    except BaseException:
        pass

    heading = startheading

    if len(path) > 1:
        for i in range(len(path) - 1):
            x = path[i][0]
            y = path[i][1]

            print(f"Current state: {(x, y)}, heading {heading}")

            # figure out direction of next node
            dx = path[i + 1][0] - x
            dy = path[i + 1][1] - y

            if abs(dx) + abs(dy) > 1:
                raise Exception("Path does not have connected nodes")

            nextheading = heading

            # figure out next heading
            if dx == 1 and dy == 0:
                nextheading = EAST
            elif dx == -1 and dy == 0:
                nextheading = WEST
            elif dx == 0 and dy == 1:
                nextheading = NORTH
            elif dx == 0 and dy == -1:
                nextheading = SOUTH

            # figure out and make turn
            turn = (nextheading - heading + 2) % 4 - 2

            if abs(turn) == 1:
                gb.turn2nextline(r, turn)

            elif abs(turn) == 2:
                gb.turn2nextline(r, turn / abs(turn))
                currentnode = getnode(x, y, nodelist)
                if currentnode.streets[(
                        heading + int(turn / abs(turn))) % 4] != NOSTREET:
                    gb.turn2nextline(r, turn / abs(turn))

            heading = nextheading

            # update graph if possible
            try:
                updategraph(canvas, nodelist, path[i], heading)
                root.update()
            except BaseException:
                pass

            returned = gb.drive(r, ultrasonic)
            if returned:
                print("Path interrupted by obstacle")
                break
            if ultrasonic and i != len(path) - 2:
                gb.nodeadvance(r)

        # update x and y to last path
        x = path[-1][0]
        y = path[-1][1]
    else:
        x = path[0][0]
        y = path[0][1]

    print(f"Arriving at desired location: {(x, y)}, heading {heading}")
    try:
        updategraph(canvas, nodelist, (x, y), heading)
        root.update()
        root.destroy()
    except BaseException:
        pass
    return (x, y, heading)


# set as standard robot
if __name__ == "__main__":

    # donemapping = False
    r = bot.defaultrobot()

    root = Tk()
    root.geometry(f'{xsize}x{ysize}')
    canvas = Canvas(root, width=xsize, height=ysize)
    canvas.pack()

    try:
        # gb.search(r)
        # gb.calibrate(r)
        betterexplore(r, root, canvas)
        print("Done exploring")
        print(f"Current Node: {currentnode}")
        print(f"Current Heading: {heading}")

        print("------------------------------------------------")
        # planmode(r, nodelist, currentnode.x, currentnode.y, heading, root, canvas)

    except BaseException as ex:
        print("Stopping due to exception: %s" % repr(ex))

    r.shutdown()

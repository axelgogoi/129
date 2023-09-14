# Written by Axel Gogoi 
# for ME/CS/EE 129 SP '21-22
# https://github.com/axelgogoi/129

import botutilities as bot
import time
import ultrasonic_behaviors as ub
import explorefinal as ex
from exploregrid import *

from maputilities import *
from mapmaker import *
from tkinter import *
import threading
import pickle

# Global variables
heading = NORTH
currentnode = None
ex.nodelist = []
ex.pausemapping = False
ex.donemapping = True
ub.scanning = False


# user input
def userloop(r):
    global currentmap
    global driving_stopflag
    global nodelist

    x = 0
    y = 0

    while True:
        # get a command from user input
        print("[h]ome, [e]xplore, [d]irectedexplore, [g]oto, [p]ause, [s]ave, [l]oad, [q]uit")
        command = input("Command?: ")

        # compare against possible commands
        if (command.lower() == 'h'):
            print('Restarting the robot at the home position')
            ex.donemapping = True
            if ex.pausemapping:
                ex.pausemapping = False
            if 'map_thread' in locals() and map_thread.is_alive():
                map_thread.join()
            print("Homing now")
            try:
                x = int(input("Starting x position: "))
                y = int(input("Starting y position: "))
                ex.heading = int(input("Starting heading: "))
            except BaseException:
                print('Invalid home, setting (x, y, heading) to (0, 0, NORTH)')
                x = 0
                y = 0
                ex.heading = NORTH
            ex.currentnode = None
            ex.nodelist = []

        elif (command.lower() == 'e'):
            print('Exploring without a target')
            ex.pausemapping = False

            if ex.donemapping:
                if 'map_thread' in locals() and map_thread.is_alive():
                    map_thread.join()
                ex.donemapping = False

                if ex.currentnode is not None:
                    x = ex.currentnode.x
                    y = ex.currentnode.y

                    if ex.heading % 4 == NORTH:
                        y = y + 1
                    elif ex.heading % 4 == WEST:
                        x = x - 1
                    elif ex.heading % 4 == SOUTH:
                        y = y - 1
                    elif ex.heading % 4 == EAST:
                        x = x + 1
                print("MAPPING NOW")

                map_thread = threading.Thread(
                    target=ex.completeexplore, args=[r, x, y])
                map_thread.start()

        elif (command.lower() == 'd'):
            print('Exploring with a target')
            try:
                xtarget = int(input("Target x position: "))
                ytarget = int(input("Target y position: "))
            except BaseException:
                print('Invalid target')
                pass

            ex.pausemapping = False

            if ex.donemapping:
                if 'map_thread' in locals() and map_thread.is_alive():
                    map_thread.join()
                ex.donemapping = False

                if ex.currentnode is not None:
                    x = ex.currentnode.x
                    y = ex.currentnode.y

                    if ex.heading % 4 == NORTH:
                        y = y + 1
                    elif ex.heading % 4 == WEST:
                        x = x - 1
                    elif ex.heading % 4 == SOUTH:
                        y = y - 1
                    elif ex.heading % 4 == EAST:
                        x = x + 1
                print("MAPPING NOW")

                map_thread = threading.Thread(
                    target=ex.completeexplore, args=[
                        r, x, y, xtarget, ytarget])
                map_thread.start()

        elif (command.lower() == 'g'):
            print('Driving to a target')
            ex.donemapping = True
            while not ex.exitflag:
                pass

            ex.planmode(
                r,
                ex.nodelist,
                ex.currentnode.x,
                ex.currentnode.y,
                ex.heading)
            print("Exiting planned driving mode")

        elif (command.lower() == 'p'):
            print("Pausing at the next intersection")
            if not ex.pausemapping:
                print("PAUSING MAPPING")
            ex.pausemapping = True

        elif (command.lower() == 's'):
            # save map to a file
            print('Saving the map...')
            with open('map.pickle', 'wb') as file:
                pickle.dump(ex.nodelist, file)

        elif (command.lower() == 'l'):
            # load map from a file
            print('Loading the map...')
            with open('map.pickle', 'rb') as file:
                ex.nodelist = pickle.load(file)

        elif (command.lower() == 'c'):
            # print current state
            print(ex.currentnode.x, ex.currentnode.y, ex.heading)
        elif (command.lower() == 'q'):
            print("Quitting...")
            break
        else:
            print("Unknown command '%s'" % command)


# Main
if __name__ == "__main__":

    # making default robot object
    r = bot.defaultrobot()

    # starting two new threads (triggering and driving)
    triggering_thread = threading.Thread(target=ub.startscanning, args=[r])
    triggering_thread.start()

    try:
        userloop(r)

    except BaseException as ex:
        print("Stopping due to exception: %s" % repr(ex))

    # rejoining threads
    ub.stopscanning()
    triggering_thread.join()

    # shutdown
    r.shutdown()

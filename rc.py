# Written by Axel Gogoi 
# for ME/CS/EE 129 SP '21-22
# https://github.com/axelgogoi/129

from tkinter import *
import time
import botutilities as bot

r = bot.defaultrobot()

F = False
B = False
L = False
R = False

v_straight = 1
v_turn = 0.5
v_turninplace = 0.5


def key_handler(event):
    global F
    global B
    global L
    global R
    global done

    key = event.keysym
    if key == 'q':
        print("Quitting RC")
        done = True
    elif key == 'w':
        F = True
    elif key == 'a':
        L = True
    elif key == 'd':
        R = True
    elif key == 's':
        B = True


def release_handler(event):
    global F
    global B
    global L
    global R
    global done

    key = event.keysym
    if key == 'q':
        done = True
    elif key == 'w':
        F = False
    elif key == 'a':
        L = False
    elif key == 'd':
        R = False
    elif key == 's':
        B = False


if __name__ == '__main__':
    root = Tk()
    done = False

    # Bind events to handlers.
    root.bind('<Key>', key_handler)
    root.bind("<KeyRelease>", release_handler)
    

    # Start the event loop.
    print("Starting RC")
    r.beep()
    r.stop()
    try:
        while not done:
            if not (F or L or R or B):
                r.stop()
            elif F and not (L or R or B):
                r.setvelAC(v_straight, 0)
            elif B and not (L or R or F):
                r.setvelAC(-v_straight, 0)
            elif L and not (B or R or F):
                r.setvelAC(v_turninplace, 90)
            elif R and not (B or L or F):
                r.setvelAC(v_turninplace, -90)
            elif F and L and not (B or R):
                r.setvelAC(v_turn, 45)
            elif F and R and not (B or L):
                r.setvelAC(v_turn, -45)
            elif B and L and not (F or R):
                r.setvelAC(-v_turn, 45)
            elif B and R and not (F or L):
                r.setvelAC(-v_turn, -45)

            # add a slight delay to smooth out the simulation
            time.sleep(0.001)
            root.update()
    except BaseException as ex:
        print("Stopping due to exception: %s" % repr(ex))

r.shutdown()
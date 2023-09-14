import botutilities as bot
from gridbehaviors import *
import time

# set as standard robot
if __name__ == "__main__":
    r = bot.defaultrobot()

    try:
        drive(r)
        check(r)
        time.sleep(1)
        turn(r, 2)
        drive(r)
        turn(r, -2)
        
    except BaseException as ex:
        print("Stopping due to exception: %s" % repr(ex))

    r.shutdown()

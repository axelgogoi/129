import botutilities as bot
from gridbehaviors import *
import time

# set as standard robot
if __name__ == "__main__":

    r = bot.defaultrobot()

    try:
        drivebehavior(r)
        checkbehavior(r)
        time.sleep(1)
        turnbehavior(r, 2)
        drivebehavior(r)
        turnbehavior(r, -2)
        
    except BaseException as ex:
        print("Stopping due to exception: %s" % repr(ex))

    r.shutdown()
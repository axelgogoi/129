# LRRRF
import botutilities as bot
from gridbehaviors import *
import time


# # set as standard robot
# if __name__ == "__main__":

#     r = bot.defaultrobot()

#     try:
#         #L
#         r.drivebehavior()
#         r.turnbehavior(1)
#         #R
#         r.drivebehavior()
#         r.turnbehavior(-1)
#         #R
#         r.drivebehavior()
#         r.turnbehavior(-1)
#         #R
#         r.drivebehavior()
#         r.turnbehavior(-1)
#         #F
#         r.drivebehavior()
#         r.drivebehavior()

#     except BaseException as ex:
#         print("Stopping due to exception: %s" % repr(ex))

#     r.shutdown()

# RLLLF

# set as standard robot
if __name__ == "__main__":

    r = bot.defaultrobot()

    try:
        #R
        r.drivebehavior()
        r.turnbehavior(-1)
        #L
        r.drivebehavior()
        r.turnbehavior(1)
        #L
        r.drivebehavior()
        r.turnbehavior(1)
        #L
        r.drivebehavior()
        r.turnbehavior(1)
        #F
        r.drivebehavior()
        r.drivebehavior()
        
    except BaseException as ex:
        print("Stopping due to exception: %s" % repr(ex))

    r.shutdown()
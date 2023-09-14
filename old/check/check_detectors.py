# The state of the detectors address
# do they work or not?
# I suppose we will see

# imports
import botutilities as bot

LEFT = 14
MIDDLE = 15
RIGHT = 18


def checksensors(r):
    while True:
        print(r.readsensors())

#
#   Main
#
# if __name__ == "__main__":

#     ############################################################
#     # Prepare the GPIO connetion (to command the motors).
#     print("Setting up the GPIO...")
    
#     # Initialize the connection to the pigpio daemon (GPIO interface).
#     io = pigpio.pi()
#     if not io.connected:
#         print("Unable to connection to pigpio daemon!")
#         sys.exit(0)

#     # Set up the three pins as input.
#     io.set_mode(LEFT, pigpio.INPUT)
#     io.set_mode(MIDDLE, pigpio.INPUT)
#     io.set_mode(RIGHT, pigpio.INPUT)

#     while True:
#         print("Left: " + str(io.read(LEFT)))
#         print("Middle: " + str(io.read(MIDDLE)))
#         print("Right: " + str(io.read(RIGHT)))
#         print("-----------------------------")

    
    # stop the interface.
    # io.stop()

#
#   Main
#

if __name__ == "__main__":

    r = bot.defaultrobot()
    
    try:
        checksensors(r)
    except BaseException as ex:
        print("Stopping due to exception: %s" % repr(ex))

    r.shutdown()

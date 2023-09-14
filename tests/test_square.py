import botutilities as bot
import time

def dosquare(r):
    for _ in range(4):
        #move forward 1 second
        r.setlinear(0.2)
        time.sleep(1)

        #turn 90 degrees
        r.turnangle(90, 0.75, k_a = 1.3)

def loopsquare(r):
    while True:
        for _ in range(4):
            #move forward 1 second
            r.setlinear(0.2)
            time.sleep(1)

            #turn 90 degrees
            r.turnangle(90, 0.75, k_a = 1.3)


if __name__ == "__main__":

    r = bot.defaultrobot()
    
    try:
        dosquare(r)
    except BaseException as ex:
        print("Stopping due to exception: %s" % repr(ex))

    r.shutdown()

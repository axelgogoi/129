import botutilities as bot
import time

r = bot.defaultrobot()

for _ in range(3):
    #move forward 1 second
    r.setlinear(0.2)
    time.sleep(1)

    #turn 120 degrees
    r.turnangle(120, 1, k_a = 1.3)

r.shutdown()


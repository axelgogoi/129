import botutilities as bot
import time

r = bot.defaultrobot()

#move forward for 1 second
r.setvel(0.3, 0)
time.sleep(5)


r.shutdown()
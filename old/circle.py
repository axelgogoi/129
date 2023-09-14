import botutilities as bot
import time

import math

r = bot.defaultrobot()

r.setvel(0.3, 180)
time.sleep(15)

r.shutdown()
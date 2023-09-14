import botutilities as bot
import time

r = bot.defaultrobot()

r.motors[0].set(1.0)
r.motors[1].set(1.0)

time.sleep(10)

r.shutdown()

import botutilities as bot
import time

r = bot.defaultrobot()

#spin for 1 second at slow speed
r.motors[0].set(0.7)
r.motors[1].set(-0.7)
time.sleep(1)

r.shutdown()

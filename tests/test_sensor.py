import pigpio

io = pigpio.pi()

print(io.read(14))
print(io.read(15))
print(io.read(16))

io.stop()

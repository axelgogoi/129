import numpy as np


angles = np.arange(0, 360, 45)
measurements = [0,  0,  1, 0, 0, 1, 0, 0]
lineindexes = []
i = 0
    
while i < len(measurements):
    print(i)
    if measurements[i] == 1:
        j = i
        indices = []
        while measurements[j] == 1:
            indices.append(j)
            j = j + 1
        lineindexes.append(int(np.median(indices)))
        i = j
    else:
        i = i + 1

print(lineindexes)

for lineindex in lineindexes:
    print(f"Line Detected at {angles[lineindex]} degrees")
    
gridangles = {0: "FORWARD", 90:  "LEFT", 180: "BACKWARD", 270: "RIGHT"}
tolerance = 45

for gridangle in gridangles:
    inrange = False
    for lineindex in lineindexes:
        if angles[lineindex] > gridangle - tolerance and angles[lineindex] < gridangle + tolerance:
            inrange = True
    if inrange:
        print(f"{gridangles[gridangle]}: {inrange}")
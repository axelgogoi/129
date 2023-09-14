# Written by Axel Gogoi 
# for ME/CS/EE 129 SP '21-22
# https://github.com/axelgogoi/129

from tkinter import *
import math

NORTH = 0
WEST = 1
SOUTH = 2
EAST = 3
HEADING = {NORTH: 'North', WEST: 'West ', SOUTH: 'South',
           EAST: 'East ', None: 'None '}

# Street status
UNKNOWN = 'Unknown   '
NOSTREET = 'NoStreet  '
UNEXPLORED = 'Unexplored'
CONNECTED = 'Connected '

UNSEEN = 0
ONDECK = 1
DONE = 2


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # # Status of streets at the intersection, in NWSE directions.
        self.streets = [UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN]
        # self.streets = streets

        # Direction to head from this intersection in planned move.
        self.status = None
        self.path = []
        
        # Set status of blocked streets
        self.blocked = [False, False, False, False]
        # self.blockedstreets = 

    # Print format.
    def __repr__(self):
        return f"Node ({self.x},{self.y})"

    def xy(self):
        return (self.x, self.y)

# returns Node object at coordinates if possible


def getnode(x, y, nodelist):
    nodes = [i for i in nodelist if i.x == x and i.y == y]
    if len(nodes) == 0:
        return None
    if len(nodes) > 1:
        raise Exception("Multiple nodes at (%2d,%2d)" % (x, y))
    return nodes[0]

# returns shortest path between nodes given a particular map


def dijkstra(nodelist, startx, starty, goalx, goaly):

    # reset status and paths of all nodes
    for n in nodelist:
        n.status = UNSEEN
        n.path = []

    startnode = getnode(startx, starty, nodelist)
    goalnode = getnode(goalx, goaly, nodelist)

    if startnode is None:
        raise Exception("Start node isn't in map")
    if goalnode is None:
        print("Goal node isn't in map")
        closestnode = None
        mindistance = math.inf
        for node in nodelist:
            xy = node.xy()

            distance = math.sqrt((goalx - xy[0])**2 + (goaly - xy[1])**2)
            if distance < mindistance:
                mindistance = distance
                closestnode = node
    
        goalnode = closestnode
    if goalnode is None:
        print("Closest node doesn't exist???")

    # assign first node and ondeck list
    startnode.status = ONDECK
    ondeck = [i for i in nodelist if i.status == ONDECK]
    for n in nodelist:
        n.path.append(startnode.xy())

    # main loop
    while len(ondeck) > 0:
        currentnode = ondeck.pop(0)

        # if at goal, stop
        if (currentnode.xy() == goalnode.xy()):
            break

        # add all neighbors (connected nodes) to ondeck
        neighbors = []
        for i in range(len(currentnode.streets)):
            if currentnode.streets[i] == CONNECTED and not currentnode.blocked[i]:
                x = currentnode.x
                y = currentnode.y

                if i % 4 == NORTH:
                    y = y + 1
                elif i % 4 == WEST:
                    x = x - 1
                elif i % 4 == SOUTH:
                    y = y - 1
                elif i % 4 == EAST:
                    x = x + 1

                neighbors.append(getnode(x, y, nodelist))

        for neighbor in neighbors:
            if neighbor.status == UNSEEN:
                # if ondeck node has no path, give it a path using current node
                neighbor.status = ONDECK
                neighbor.path = []
                neighbor.path.extend(currentnode.path)
                neighbor.path.append(neighbor.xy())
            elif neighbor.status == ONDECK:
                # if ondeck node has a path, replace with path using current
                # node if it is better
                oldcost = len(neighbor.path[:-1])
                newcost = len(currentnode.path)

                if newcost < oldcost:
                    neighbor.path = []
                    neighbor.path.extend(currentnode.path)
                    neighbor.path.append(neighbor.xy())
                    ondeck.remove(neighbor.xy())
                    ondeck.insert(0, neighbor.xy())

        # set current node to processed
        currentnode.status = DONE

        # recalculate and sort ondeck list
        ondeck = [i for i in nodelist if i.status == ONDECK]
        ondeck.sort(key=lambda node: len(node.path))

    print("Path to goal: " + str(goalnode.path))
    return goalnode.path


if __name__ == "__main__":

    a = Node(0, 0, streets=[CONNECTED, NOSTREET, NOSTREET, NOSTREET])
    b = Node(0, 1, streets=[CONNECTED, NOSTREET, CONNECTED, CONNECTED])
    c = Node(0, 2, streets=[NOSTREET, NOSTREET, CONNECTED, CONNECTED])
    d = Node(1, 2, streets=[NOSTREET, CONNECTED, CONNECTED, NOSTREET])
    e = Node(1, 1, streets=[CONNECTED, CONNECTED, NOSTREET, NOSTREET])

    nodelist = [a, b, c, d, e]

    dijkstra(nodelist, a.x, a.y, e.x, e.y)

    dijkstra(nodelist, e.x, e.y, c.x, c.y)

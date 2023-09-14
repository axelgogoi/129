# Written by Axel Gogoi 
# for ME/CS/EE 129 SP '21-22
# https://github.com/axelgogoi/129

from tkinter import *
from maputilities import *

xsize = 800
ysize = 800

x0 = xsize / 2
y0 = ysize / 2

spacing = 30
nodesize = 8
robotsize = 6
connectionsize = 5
headinglength = 10

spacing2 = 8
spacing3 = 15

handles = []

def draw_node(canvas, node):
    x = spacing * node.x
    y = spacing * node.y
    nodehandle = canvas.create_oval(
        x0 + x - nodesize,
        y0 - y - nodesize,
        x0 + x + nodesize,
        y0 - y + nodesize,
        fill="#000000",
        width=0)

    nodesubhandles = []

    for i in range(len(node.streets)):
        xc = x
        yc = y
        if i % 4 == NORTH:
            yc = y + spacing2
        elif i % 4 == WEST:
            xc = x - spacing2
        elif i % 4 == SOUTH:
            yc = y - spacing2
        elif i % 4 == EAST:
            xc = x + spacing2

        if node.streets[i] == UNEXPLORED:
            connection = canvas.create_oval(
                x0 + xc - connectionsize,
                y0 - yc - connectionsize,
                x0 + xc + connectionsize,
                y0 - yc + connectionsize,
                fill="#0000FF",
                width=0)
            nodesubhandles.append(connection)
        elif node.streets[i] == UNKNOWN:
            connection = canvas.create_oval(
                x0 + xc - connectionsize,
                y0 - yc - connectionsize,
                x0 + xc + connectionsize,
                y0 - yc + connectionsize,
                fill="#FF0000",
                width=0)
            nodesubhandles.append(connection)

    for i in range(len(node.blocked)):
        xc = x
        yc = y
        if i % 4 == NORTH:
            yc = y + spacing3
        elif i % 4 == WEST:
            xc = x - spacing3
        elif i % 4 == SOUTH:
            yc = y - spacing3
        elif i % 4 == EAST:
            xc = x + spacing3

        if node.blocked[i] == True:
            connection = canvas.create_oval(
                x0 + xc - connectionsize,
                y0 - yc - connectionsize,
                x0 + xc + connectionsize,
                y0 - yc + connectionsize,
                fill="#FFA500",
                width=0)
            nodesubhandles.append(connection)

    return (nodehandle, nodesubhandles)


def draw_links(canvas, nodelist):
    links = []
    linkhandles = []

    for node in nodelist:
        for i in range(len(node.streets)):
            if node.streets[i] == CONNECTED:
                x2 = node.x
                y2 = node.y
                if i % 4 == NORTH:
                    y2 = y2 + 1
                elif i % 4 == WEST:
                    x2 = x2 - 1
                elif i % 4 == SOUTH:
                    y2 = y2 - 1
                elif i % 4 == EAST:
                    x2 = x2 + 1

                link = (node.xy(), (x2, y2))
                reverselink = ((x2, y2), node.xy())

                if not (link in links or reverselink in links):
                    links.append(link)

    for link in links:
        x1 = x0 + spacing * link[0][0]
        y1 = y0 - spacing * link[0][1]
        x2 = x0 + spacing * link[1][0]
        y2 = y0 - spacing * link[1][1]
        linkhandle = canvas.create_line(
            x1, y1, x2, y2, fill="#000000", width=3)
        linkhandles.append(linkhandle)

    return linkhandles

def drawrobot(canvas, xy, heading):
    x = spacing * xy[0]
    y = spacing * xy[1]
    robothandle1 = canvas.create_oval(
        x0 + x - robotsize,
        y0 - y - robotsize,
        x0 + x + robotsize,
        y0 - y + robotsize,
        fill="#00FF00",
        width=0)

    xh = x
    yh = y
    
    if heading % 4 == NORTH:
        yh = yh + headinglength
    elif heading % 4 == WEST:
        xh = xh - headinglength
    elif heading % 4 == SOUTH:
        yh = yh - headinglength
    elif heading % 4 == EAST:
        xh = xh + headinglength
    else:
        raise Exception("This can't be")

    robothandle2 = canvas.create_line(
            x + x0, -y + y0, xh + x0, -yh + y0, fill="#00FF00", width=5)

    return (robothandle1, robothandle2)

def updategraph(canvas, nodelist, robotxy, heading):
    for handle in handles:
        canvas.delete(handle)

    for node in nodelist:
        nodehandle = draw_node(canvas, node)
        handles.append(nodehandle[0])
        for nodesubhandle in nodehandle[1]:
            handles.append(nodesubhandle)

    linkhandles = draw_links(canvas, nodelist)
    for linkhandle in linkhandles:
        handles.append(linkhandle)

    robothandles = drawrobot(canvas, robotxy, heading)
    for robothandle in robothandles:
        handles.append(robothandle)

if __name__ == '__main__':
    root = Tk()
    root.geometry(f'{xsize}x{ysize}')
    canvas = Canvas(root, width=xsize, height=ysize)
    canvas.pack()

    # a = Node(0, 0)
    # b = Node(0, 1)
    # c = Node(0, 2)
    # d = Node(1, 2)
    # e = Node(1, 1)

    a = Node(0, 0, streets=[CONNECTED, NOSTREET, UNKNOWN, NOSTREET])
    b = Node(0, 1, streets=[CONNECTED, NOSTREET, CONNECTED, CONNECTED])
    c = Node(0, 2, streets=[NOSTREET, NOSTREET, CONNECTED, CONNECTED])
    d = Node(1, 2, streets=[NOSTREET, CONNECTED, CONNECTED, NOSTREET])
    e = Node(1, 1, streets=[CONNECTED, CONNECTED, NOSTREET, NOSTREET])

    nodelist = [a, b, c, d, e]

    while True:
        updategraph(canvas, nodelist)
        root.update()

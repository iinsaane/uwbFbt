import math
import sys
import threading
import time
import tkinter as tk

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits import mplot3d
from serial import Serial

cross1 = lambda x,y:np.cross(x,y) # cross workaround
normalize = lambda x:x/np.linalg.norm(x) # normalize vector

# initialize the graph
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
plt.show(block=False)

# tkinter window
root = tk.Tk()
root.geometry("200x500")
root.title("Tag Data")


class Tag:
    def __init__(self, id):
        self.smoothingSteps = 5
        self.maxDistance = 100
        self.minDistance = 0
        self.speed = 0.5
        self.locationHistory = []

        self.distance1 = [0, 0, 0, 0, 0]
        self.distance2 = [0, 0, 0, 0, 0]
        self.distance3 = [0, 0, 0, 0, 0]

        self.lastRead1 = time.time()
        self.lastRead2 = time.time()
        self.lastRead3 = time.time()

        self.belowPlane = True
        self.position = {"x": 0, "y": 0, "z": 0}  # default position
        self.id = id

        # anchor position
        self._anchor1 = {"x": 100, "y": 0, "z": 100}
        self._anchor2 = {"x": 0, "y": 0, "z": 100}
        self._anchor3 = {"x": 100, "y": 0, "z": 200}

    def multilateration(self):

        if (sum(self.distance1) == 0 or sum(self.distance2) == 0 or sum(self.distance3) == 0):
            return

        # unpack the anchor data
        A1 = np.array([self._anchor1["x"], self._anchor1["y"], self._anchor1["z"]])
        A2 = np.array([self._anchor2["x"], self._anchor2["y"], self._anchor2["z"]])
        A3 = np.array([self._anchor3["x"], self._anchor3["y"], self._anchor3["z"]])

        # unpack the distance data
        r1 = self.getDistance1()
        r2 = self.getDistance2()
        r3 = self.getDistance3()

        # bring the anchors to the origin
        offset = A1
        A2 = A2 - offset
        A3 = A3 - offset
        A1 = A1 - offset

        # get the rotation matrix of the plane
        v1 = A2
        v2 = A3
        if (v1==v2).all():
            print("Error: anchors are in a line")
            exit()

        matrix = np.zeros((3,3))
        matrix[0] = normalize(v1)
        matrix[2] = normalize(cross1(v1,v2))
        matrix[1] = normalize(cross1(matrix[2],matrix[0]))
        
        # rotate the points
        A1 = np.dot(matrix, A1)
        A2 = np.dot(matrix, A2)
        A3 = np.dot(matrix, A3)

        # round the points to the nearest integer
        A1 = np.rint(A1)
        A2 = np.rint(A2)
        A3 = np.rint(A3)

        # run the trilateration algorithm
        U = A2[0]
        Vx = A3[0]
        Vy = A3[1]
        try:
            x = (r1**2 - r2**2 + U**2) / (2*U)
            y = (r1**2 - r3**2 + Vx**2 + Vy**2 - 2*Vx*x) / (2*Vy)
            z = (r1**2 - x**2 - y**2)**0.5
        except:
            print("Error: point is out of range")
            pass
        
        if (self.belowPlane):
            z = -z
        P2 = np.array([x, y, z])

        # rotate the point back
        P2 = np.dot(np.linalg.inv(matrix), P2)

        # translate the point back
        P2 = P2 + offset

        # return if the position is not a number
        if (math.isnan(P2[0]) or math.isnan(P2[1]) or math.isnan(P2[2])):
            return

        # update the position
        position = {"x": P2[0], "y": P2[1], "z": P2[2]}
        nextPosition = self.lerp(self.position, position, self.speed)
        self.position = nextPosition


    def lerp(self, position, target, amount): # position and target are x y z dictionaries
        # make sure both positions are valid
        if (math.isnan(position["x"]) or math.isnan(position["y"]) or math.isnan(position["z"])):
            return target
        
        if (math.isnan(target["x"]) or math.isnan(target["y"]) or math.isnan(target["z"])):
            return position
        
        return {
            "x": position["x"] + (target["x"] - position["x"]) * amount,
            "y": position["y"] + (target["y"] - position["y"]) * amount,
            "z": position["z"] + (target["z"] - position["z"]) * amount,
        } # if amount is 0, return position, if amount is 1, return target. also allows overshooting and going negative

    def setDistance1(self, distance):
        self.distance1.pop(0)
        self.distance1.append(distance)
        self.lastRead1 = time.time()
        self.multilateration()

    def setDistance2(self, distance):
        self.distance2.pop(0)
        self.distance2.append(distance)
        self.lastRead2 = time.time()
        self.multilateration()

    def setDistance3(self, distance):
        self.distance3.pop(0)
        self.distance3.append(distance)
        self.lastRead3 = time.time()
        self.multilateration()

    def getDistance1(self):
        # copy the arrat to a new array
        distances = self.distance1.copy()
        distances.sort()
        distances.pop(0)
        distances.pop(-1)
        # calculate the average
        return sum(distances) / len(distances)

    def getDistance2(self):
        # copy the arrat to a new array
        distances = self.distance2.copy()
        distances.sort()
        distances.pop(0)
        distances.pop(-1)
        # calculate the average
        return sum(distances) / len(distances)

    def getDistance3(self):
        # copy the arrat to a new array
        distances = self.distance3.copy()
        distances.sort()
        distances.pop(0)
        distances.pop(-1)
        # calculate the average
        return sum(distances) / len(distances)


def read_serial_data(ser):
    # print("Reading data from ", ser.name)
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode().strip()
            tag_id, distance = 0, 0
            try:
                # split the data
                first, second = data.split(",")
                tag_id = int(first.strip())
                distance = max(int(second), 0)
            except:
                print("Error: ", sys.exc_info()[0])
                continue
                pass
            else:
                # print("Success: ", f'{ser.name}: {tag_id}, {distance}')
                pass

            anchormap = {"COM10": 0, "COM11": 1, "COM12": 2}

            # check if the tag is already in the list
            for tag in tags:
                if tag.id == tag_id:
                    function = "setDistance" + str(anchormap[ser.name] + 1)
                    getattr(tag, function)(distance)
                    # tag.multilateration()
                    break

            else:  # if not, create a new tag
                tag = Tag(tag_id)
                function = "setDistance" + str(anchormap[ser.name] + 1)
                getattr(tag, function)(distance)
                tags.append(tag)
                print("New tag: ", tag.id)


def render():
    ax.clear()

    # plot the anchors
    ax.scatter(100, 0, 100, c='r', marker='o')
    ax.text(100, 0, 100, 'A1')

    ax.scatter(0, 0, 100, c='r', marker='o')
    ax.text(0, 0, 100, 'A2')

    ax.scatter(100, 0, 200, c='r', marker='o')
    ax.text(100, 0, 200, 'A3')

    # check if there is any tag
    if not tags:
        # update the graph
        plt.draw()
        plt.pause(0.1)
        return

    # plot the tags
    for tag in tags:
        ax.scatter(tag.position["x"], tag.position["y"],
                   tag.position["z"], c='b', marker='o')

    # update the graph
    ax.set_xlim([-100, 100])
    ax.set_ylim([-200, 0])
    ax.set_zlim([0, 200])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.draw()
    plt.pause(0.1)

    # tkinter window
    # clear the window
    for label in root.grid_slaves():
        label.destroy()

    # tags
    for tag in tags:
        titlecolor = "red" if int(time.time() - tag.lastRead1) > 1 or int(time.time(
        ) - tag.lastRead2) > 1 or int(time.time() - tag.lastRead3) > 1 else "green"
        label = tk.Label(root, text=f"Tag {tag.id}\n",
                         fg=titlecolor)
        label.grid()

        distance = int(tag.getDistance1())
        lastread = int(time.time() - tag.lastRead1)
        fg = "red" if lastread > 1 else "green"
        label = tk.Label(root, text=f"Distance1: {distance}\t last read 1: {lastread}\n",
                         fg=fg)
        label.grid()

        distance = int(tag.getDistance2())
        lastread = int(time.time() - tag.lastRead2)
        fg = "red" if lastread > 1 else "green"
        label = tk.Label(root, text=f"Distance2: {distance}\t last read 2: {lastread}\n",
                         fg=fg)
        label.grid()

        distance = int(tag.getDistance3())
        lastread = int(time.time() - tag.lastRead3)
        fg = "red" if lastread > 1 else "green"
        label = tk.Label(root, text=f"Distance3: {distance}\t last read 3: {lastread}\n",
                         fg=fg)
        label.grid()

        label = tk.Label(root, text=f"{'-'*40}")
        label.grid()
    root.update()


def main():
    global tags
    tags = []

    # open serial ports
    Anchor1 = Serial(
        port="COM10",
        baudrate=115200,
        bytesize=8,
        stopbits=1,
        parity="N",
    )

    Anchor2 = Serial(
        port="COM11",
        baudrate=115200,
        bytesize=8,
        stopbits=1,
        parity="N"
    )

    Anchor3 = Serial(
        port="COM12",
        baudrate=115200,
        bytesize=8,
        stopbits=1,
        parity="N"
    )

    # create threads to read serial data
    thread1 = threading.Thread(
        target=read_serial_data, args=(Anchor1,))
    thread2 = threading.Thread(
        target=read_serial_data, args=(Anchor2,))
    thread3 = threading.Thread(
        target=read_serial_data, args=(Anchor3,))

    # start threads
    thread1.start()
    thread2.start()
    thread3.start()

    # main loop
    while True:
        # print(tags)

        # graph the data
        render()

        # wait for some time
        time.sleep(0.05)


if __name__ == "__main__":
    main()

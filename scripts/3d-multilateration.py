import sys
import serial
import math
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import time

# serial port queue
queue = []
needsUpdate = False

# Initialize variables to store the distance from each device.
tags = []
# tags = [{
#   "id": 1,
#   "distance": {
#    "Anchor1": 0,
#    "Anchor2": 0,
#    "Anchor3": 0
# }
#   "position": {
#     "x": 0,
#     "y": 0,
#     "z": 0
#   }
# }]

# define anchor positions
anchor1 = {"x": 0, "y": 0, "z": 0}
anchor2 = {"x": 50, "y": 0, "z": 0}
anchor3 = {"x": 50, "y": 75, "z": 0}

U = anchor2["x"]-anchor1["x"]

Vx = anchor3["x"]-anchor1["x"]
Vy = anchor3["y"]-anchor1["y"]

print(U, Vx, Vy)

# define the graph
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([0, 100])
ax.set_ylim([0, 100])
ax.set_zlim([0, 100])
plt.show(block=False)


def update_plot():
    try:
        # calculate the position for each tag
        for tag in tags:
            tag["position"] = threeDimensionalTrilateration(
                tag["distance"]["Anchor1"], tag["distance"]["Anchor2"], tag["distance"]["Anchor3"])
            # print("got position for ", tag["id"])
    except:
        print("error calculating position for ", tag["distance"])
        # remove the tag from the list
        tags.remove(tag)
        return

    # clear the plot
    ax.clear()

    # plot the position of each anchor
    try:
        ax.scatter(anchor1["x"], anchor1["y"], anchor1["z"])
        ax.text(anchor1["x"], anchor1["y"], anchor1["z"], "Anchor1")
        ax.scatter(anchor2["x"], anchor2["y"], anchor2["z"])
        ax.text(anchor2["x"], anchor2["y"], anchor2["z"], "Anchor2")
        ax.scatter(anchor3["x"], anchor3["y"], anchor3["z"])
        ax.text(anchor3["x"], anchor3["y"], anchor3["z"], "Anchor3")
    except:
        print("couldnt display anchor")

    # plot the position of each tag
    try:
        for tag in tags:
            # print("tag: ", tag["position"])
            ax.scatter(tag["position"]["x"], tag["position"]["y"],
                       tag["position"]["z"])
            ax.text(tag["position"]["x"], tag["position"]["y"],
                    tag["position"]["z"], tag["id"])
    except:
        print("couldnt display tag")

    # draw lines between the anchors and the tags
    try:
        for tag in tags:
            ax.plot([anchor1["x"], tag["position"]["x"]], [
                    anchor1["y"], tag["position"]["y"]], [anchor1["z"], tag["position"]["z"]])
            ax.plot([anchor2["x"], tag["position"]["x"]], [
                    anchor2["y"], tag["position"]["y"]], [anchor2["z"], tag["position"]["z"]])
            ax.plot([anchor3["x"], tag["position"]["x"]], [
                    anchor3["y"], tag["position"]["y"]], [anchor3["z"], tag["position"]["z"]])
    except:
        print("couldnt display lines")

    ax.set_xlim([-100, 100])
    ax.set_ylim([-100, 100])
    ax.set_zlim([0, 200])
    plt.pause(0.01)


# Define the serial port settings for both devices.
Anchor1 = serial.Serial(
    port="COM12",
    baudrate=115200,
    bytesize=8,
    stopbits=1,
    parity="N"
)

Anchor2 = serial.Serial(
    port="COM14",
    baudrate=115200,
    bytesize=8,
    stopbits=1,
    parity="N"
)

Anchor3 = serial.Serial(
    port="COM15",
    baudrate=115200,
    bytesize=8,
    stopbits=1,
    parity="N"
)

# process the serial data


def process_serial_data(data, anchor):
    try:
        first, second = data.split(",")
        print("anchor: ", anchor, "\tfirst: ", first, "\tsecond: ", second)
        if (first == "connected"):
            print("attemptint to connect tag " + second)
            # check if the tag is already in the list
            for tag in tags:
                if (tag["id"] == second):
                    return

            tags.append({
                "id": second,
                "distance": {
                        "Anchor1": None,
                        "Anchor2": None,
                        "Anchor3": None
                        },
                "position": {
                    "x": None,
                    "y": None,
                    "z": None
                }
            })
            print("connected tag " + second)

        elif (first == "disconnected"):
            # remove the tag from the list
            for tag in tags:
                if (tag["id"] == second):
                    tags.remove(tag)
            print("disconnected tag " + second)

        else:
            # check if the tag is in the list. add it if it isn't
            for tag in tags:
                if (tag["id"] == first):
                    break
            else:
                tags.append({
                    "id": first,
                    "distance": {
                        "Anchor1": None,
                        "Anchor2": None,
                        "Anchor3": None
                    },
                    "position": {
                        "x": None,
                        "y": None,
                        "z": None
                    }
                })
                print("added tag " + first)

            # update the distance
            for tag in tags:
                if (tag["id"] == first):
                    tag["distance"][anchor] = int(second)
            needsUpdate = True
            # print("anchor: ", anchor, "\tdistance: ", int(second))
    except:
        print("Error processing serial data for anchor " + anchor)


def twoDimensionalTrilateration(r1, r2):
    try:
        tagX = (r1 ** 2 - r2 ** 2 + U ** 2) / (2 * U)
        tagY = math.sqrt(abs(r1 ** 2 - tagX ** 2))
        position = {"x": tagX, "y": tagY}
        return position

    except:
        raise Exception("Error calculating position")


def threeDimensionalTrilateration(r1, r2, r3):
    try:
        tagX = (r1 ** 2 - r2 ** 2 + U ** 2) / (2 * U)
        tagY = (r1**2 - r3**2 + Vx**2 + Vy**2 - 2*tagX*Vx) / (2*Vy)
        tagZ = math.sqrt(abs(r1 ** 2 - tagX ** 2 - tagY ** 2))
        # print("tagX: " + str(tagX), "tagY: " + str(tagY), "tagZ: " + str(tagZ))

        position = {"x": tagX, "y": tagY, "z": tagZ}
        return position

    except:
        raise Exception("Error calculating position")


# Set up event listeners for data coming in on each serial port.
# When data is received, parse the device address and distance from the data string.
# If the device address matches the expected value, store the distance and check if we have data from both devices.
# If we have data from both devices, calculate the tag position and print it to the console.
while True:
    try:
        # anchor 1
        data1 = Anchor1.readline().decode("utf-8").strip()
        if (data1):
            process_serial_data(data1, "Anchor1")

        # anchor 2
        data2 = Anchor2.readline().decode("utf-8").strip()
        if (data2):
            process_serial_data(data2, "Anchor2")

        # anchor 3
        data3 = Anchor3.readline().decode("utf-8").strip()
        if (data3):
            process_serial_data(data3, "Anchor3")

        if needsUpdate or True:

            # update the plot
            try:
                update_plot()
            except:
                print("Error updating plot")

            # finish updating
            needsUpdate = False

        # time.sleep(0.1)
    except:
        print("Error")
        time.sleep(0.3)
        pass

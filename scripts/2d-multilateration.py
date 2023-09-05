import sys
import serial
import math
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import time

# define anchor positions
anchor1 = {"x": 0, "y": 0, "z": 0}
anchor2 = {"x": 50, "y": 0, "z": 0}

U = math.sqrt((anchor2["x"] - anchor1["x"]) ** 2 +
              (anchor2["y"] - anchor1["y"]) ** 2)

print(U)

# define the graph
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([0, 200])
ax.set_ylim([0, 200])
ax.set_zlim([0, 200])
plt.show(block=False)


def update_plot():
    tag_position = twoDimensionalTrilateration(distance12, distance14)

    # clear the plot
    ax.clear()

    # anchor 1
    ax.scatter(anchor1['x'], anchor1['y'], anchor1['z'])
    ax.text(anchor1['x'], anchor1['y'], anchor1['z'], "A1")

    # anchor 2
    ax.scatter(anchor2['x'], anchor2['y'], anchor2['z'])
    ax.text(anchor2['x'], anchor2['y'], anchor2['z'], "A2")

    # point
    ax.scatter(tag_position['x'], tag_position['y'], 0)
    ax.text(tag_position['x'], tag_position['y'], 0, "P")

    ax.set_xlim([-200, 200])
    ax.set_ylim([-200, 200])
    plt.pause(0.01)


# Define the serial port settings for both devices.
port12 = serial.Serial(
    port="COM12",
    baudrate=115200,
    bytesize=8,
    stopbits=1,
    parity="N"
)

port14 = serial.Serial(
    port="COM14",
    baudrate=115200,
    bytesize=8,
    stopbits=1,
    parity="N"
)

# Define a function to perform trilateration based on two distances and a known distance between the devices.


def twoDimensionalTrilateration(r1, r2):
    try:
        tagX = (r1 ** 2 - r2 ** 2 + U ** 2) / (2 * U)
        try:
            tagY = math.sqrt(abs(r1 ** 2 - tagX ** 2))
        except:
            print("Error calculating tag position: ")
        position = {"x": tagX, "y": tagY}
    except:
        pass
    return position


def threeDimensionalTrilateration(r1, r2, r3):
    pass


# Initialize variables to store the distance from each device.
distance12 = 0
distance14 = 0
needsUpdate = False

# Set up event listeners for data coming in on each serial port.
# When data is received, parse the device address and distance from the data string.
# If the device address matches the expected value, store the distance and check if we have data from both devices.
# If we have data from both devices, calculate the tag position and print it to the console.
while True:
    try:
        data12 = port12.readline().decode().strip()
        data14 = port14.readline().decode().strip()

        if data12:
            deviceAddress, distance = data12.split(", ")
            distance12 = int(distance)
            needsUpdate = True
            print("Distance 12: " + str(distance12))

        if data14:
            deviceAddress, distance = data14.split(", ")
            distance14 = int(distance)
            needsUpdate = True
            print("Distance 14: " + str(distance14))

        if distance12 and distance14 and needsUpdate:

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

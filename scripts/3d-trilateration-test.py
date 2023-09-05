import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

# define the graph
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
# ax.set_xlim([0, 100])
# ax.set_ylim([0, 100])
# ax.set_zlim([0, 100])
plt.show(block=False)


# def threeDimensionalTrilateration(r1, r2, r3):
#     try:
#         tagX = (r1 ** 2 - r2 ** 2 + U ** 2) / (2 * U)
#         tagY = (r1**2 - r3**2 + Vx**2 + Vy**2 - 2*tagX*Vx) / (2*Vy)
#         tagZ = math.sqrt(abs(r1 ** 2 - tagX ** 2 - tagY ** 2))
#         # print("tagX: " + str(tagX), "tagY: " + str(tagY), "tagZ: " + str(tagZ))

#         position = {"x": tagX, "y": tagY, "z": tagZ}
#         return position

# anchor1 = {"x": 0, "y": 0, "z": 0}
# anchor2 = {"x": 50, "y": 0, "z": 0}
# anchor3 = {"x": 50, "y": 75, "z": 0}

# U = anchor2["x"]-anchor1["x"]

# Vx = anchor3["x"]-anchor1["x"]
# Vy = anchor3["y"]-anchor1["y"]


#     except:
#         raise Exception("Error calculating position")
def multilateration(anchor1, anchor2, anchor3):
    # unpack the anchor data
    ax, ay, az, r1 = anchor1
    bx, by, bz, r2 = anchor2
    cx, cy, cz, r3 = anchor3

    # calculate distances between anchors on the x, y, and z axes, and total distance between anchors
    ab = [bx - ax, by - ay, bz - az,
          math.sqrt((bx - ax) ** 2 + (by - ay) ** 2 + (bz - az) ** 2)]
    ac = [cx - ax, cy - ay, cz - az,
          math.sqrt((cx - ax) ** 2 + (cy - ay) ** 2 + (cz - az) ** 2)]
    bc = [cx - bx, cy - by, cz - bz,
          math.sqrt((cx - bx) ** 2 + (cy - by) ** 2 + (cz - bz) ** 2)]

    # multilateration
    tagX = (r1 ** 2 - r2 ** 2 + ab[0] ** 2) / (2 * ab[0])
    tagY = (r1**2 - r3**2 + ac[0]**2 + ac[1]**2 - 2*tagX*ac[0]) / (2*ac[1])
    tagZ = math.sqrt(abs(r1 ** 2 - tagX ** 2 - tagY ** 2))

    # return the two possible solutions
    return [(ax + tagX, ay + tagY, az + tagZ), (ax + tagX, ay + tagY, az - tagZ)]


anchor1 = [0, 0, 0, 100.0]  # [x, y, z, dist]
anchor2 = [50.0, 0, 0.0, 100.0]
anchor3 = [50, 75, 0.0, 100.0]

location = multilateration(anchor1, anchor2, anchor3)
print(location)

# plot the anchors with labels
ax.scatter(anchor1[0], anchor1[1], anchor1[2], color='r', marker='o')
ax.text(anchor1[0], anchor1[1], anchor1[2], "Anchor1")

ax.scatter(anchor2[0], anchor2[1], anchor2[2], color='r', marker='o')
ax.text(anchor2[0], anchor2[1], anchor2[2], "Anchor2")

ax.scatter(anchor3[0], anchor3[1], anchor3[2], color='r', marker='o')
ax.text(anchor3[0], anchor3[1], anchor3[2], "Anchor3")

# plot the two possible solutions location[0], location[1]
ax.scatter(location[0][0], location[0][1],
           location[0][2], color='b', marker='o')
ax.text(location[0][0], location[0][1], location[0][2], "Solution1")

ax.scatter(location[1][0], location[1][1],
           location[1][2], color='b', marker='o')
ax.text(location[1][0], location[1][1], location[1][2], "Solution2")

# draw the lines between the anchors and the solutions
ax.plot([anchor1[0], location[0][0]], [anchor1[1], location[0][1]],
        [anchor1[2], location[0][2]], color='g')
ax.plot([anchor2[0], location[0][0]], [anchor2[1], location[0][1]],
        [anchor2[2], location[0][2]], color='g')
ax.plot([anchor3[0], location[0][0]], [anchor3[1], location[0][1]],
        [anchor3[2], location[0][2]], color='g')


# calculate distance between each anchor and the fisrt solution for testing purposes
dist1 = math.sqrt((location[0][0] - anchor1[0]) ** 2 + (location[0]
                  [1] - anchor1[1]) ** 2 + (location[0][2] - anchor1[2]) ** 2)
dist2 = math.sqrt((location[0][0] - anchor2[0]) ** 2 + (location[0]
                  [1] - anchor2[1]) ** 2 + (location[0][2] - anchor2[2]) ** 2)
dist3 = math.sqrt((location[0][0] - anchor3[0]) ** 2 + (location[0]
                  [1] - anchor3[1]) ** 2 + (location[0][2] - anchor3[2]) ** 2)

print(f"dist1: {dist1}, dist2: {dist2}, dist3: {dist3}")


plt.draw()

while (True):
    plt.pause(0.1)

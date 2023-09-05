import math

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

cross1 = lambda x,y:np.cross(x,y) # cross workaround
normalize = lambda x:x/np.linalg.norm(x) # normalize vector


# horizontal anchors
# A1 = [0, 0, 200]
# A2 = [100, 0, 200]
# A3 = [0, 100, 200]

# vertical anchors
A1 = [0, 0, 100]
A2 = [100, 0, 100]
A3 = [100, 0, 200]

# random anchors using numpy
# A1 = np.random.randint(0, 200, size=3)
# A2 = np.random.randint(0, 200, size=3)
# A3 = np.random.randint(0, 200, size=3)

A1 = np.array(A1)
A2 = np.array(A2)
A3 = np.array(A3)

# points to be located ( for testing )
P1 = np.array([0, 0, 0])

# get distances from points to anchors
r1 = ((P1[0]-A1[0])**2 + (P1[1]-A1[1])**2 + (P1[2]-A1[2])**2)**0.5
r2 = ((P1[0]-A2[0])**2 + (P1[1]-A2[1])**2 + (P1[2]-A2[2])**2)**0.5
r3 = ((P1[0]-A3[0])**2 + (P1[1]-A3[1])**2 + (P1[2]-A3[2])**2)**0.5

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
    print("Error: ", A1, A2, A3, P1)
    pass

P2 = np.array([x, y, z])
P2n = np.array([x, y, -z])

# rotate the point back
P2 = np.dot(np.linalg.inv(matrix), P2)
P2n = np.dot(np.linalg.inv(matrix), P2n)

# translate the point back
P2 = P2 + offset
P2n = P2n + offset

print ("P1: ", P1)
print ("P2: ", P2)
print ("P2n: ", P2n)



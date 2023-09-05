import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import time

# Create figure and 3D axes
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Define initial point coordinates
x, y, z = 1, 1, 1

# Plot the initial point
ax.scatter(x, y, z)

# Loop to update the z-coordinate and replot the point
while True:
    # Update the z-coordinate
    z += 1

    # Clear the plot and plot the updated point
    ax.clear()
    ax.scatter(x, y, z)

    # Set axis limits
    ax.set_xlim([-5, 5])
    ax.set_ylim([-5, 5])
    ax.set_zlim([-5, 5])

    # Pause for 1 second before updating the plot again
    plt.pause(1)

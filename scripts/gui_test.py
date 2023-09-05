import tkinter as tk
from datetime import datetime, timedelta
import time

print(time.time())

# Sample data
tags = [{'id': 1, 'distance1': 10, 'lastread1': '2022-03-26 12:34:56', 'distance2': 20, 'lastread2': '2022-03-25 12:34:56', 'distance3': 30, 'lastread3': '2022-03-24 12:34:56'},
        {'id': 2, 'distance1': 40, 'lastread1': '2022-03-26 12:34:56', 'distance2': 50, 'lastread2': '2022-03-25 12:34:56', 'distance3': 60, 'lastread3': '2022-03-24 12:34:56'}]

# Define a function to update the lastread1 value of each tag


def update_lastread1():
    for tag in tags:
        lastread1 = datetime.strptime(tag['lastread1'], '%Y-%m-%d %H:%M:%S')
        lastread1 += timedelta(seconds=1)
        tag['lastread1'] = lastread1.strftime('%Y-%m-%d %H:%M:%S')

# Define a function to render the tags in the tkinter window


def render_tags():
    # Remove any existing labels from the window
    for label in root.grid_slaves():
        label.destroy()

    # Create a label for each tag
    for tag in tags:
        label = tk.Label(root, text=f"Tag {tag['id']}\n"
                         f"Distance1: {tag['distance1']}\t last read 1: {tag['lastread1']}\n"
                         f"Distance2: {tag['distance2']}\t last read 2: {tag['lastread2']}\n"
                         f"Distance3: {tag['distance3']}\t last read 3: {tag['lastread3']}\n"
                         f"{'-'*40}")
        label.grid()


# Create a new tkinter window
root = tk.Tk()
root.geometry("300x500")
root.title("Tag Data")

# Define a function to update the tags and render them in the window


def update_and_render():
    update_lastread1()
    render_tags()
    # Schedule the next update after 1000ms (1 second)
    root.after(1000, update_and_render)


# Start the update/render loop
update_and_render()

# Run the tkinter event loop
root.mainloop()

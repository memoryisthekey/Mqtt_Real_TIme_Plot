import tkinter as tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import paho.mqtt.client as mqtt
global orientation_data
global orientation_data_force

# MQTT configuration
#mqtt_broker_host = "localhost"
mqtt_broker_host='0.0.0.0'

mqtt_topic = "inigo"
mqtt_force_topic = "force"

# Variables to store orientation data

fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))
#fig, ax = plt.subplots(111, projection='3d')


# Callback function to handle MQTT message reception
def on_message(client, userdata, message):
    global orientation_data
    payload = message.payload.decode()
    # Assuming payload is in the format "u,v,w" where u, v, and w are orientation values
    u, v, w = map(float, payload.split(","))
    orientation_data["u"] = u
    orientation_data["v"] = v
    orientation_data["w"] = w
    return u, v, w

def on_message_force(client, userdata, message):
    global orientation_data_force
    payload = message.payload.decode()
    # Assuming payload is in the format "u,v,w" where u, v, and w are orientation values
    u, v, w = map(float, payload.split(","))
    orientation_data_force["x"] = u
    orientation_data_force["y"] = v
    orientation_data_force["z"] = w
    return 


# Create a function to update the 3D quiver plot with MQTT data
def update_plot():
    # Clear the previous plot
    global a
    global b
    global c
    # Set the position of the arrow
    x = 0
    y = 0
    z = 0
     # Set axis labels

    # Use orientation data from MQTT
    u = orientation_data["u"]
    v = orientation_data["v"]
    w = orientation_data["w"]
    a = u
    b = v
    c = w
    print({"u": u, "v": v, "w": w})
    # Create the 3D quiver plot with the received orientation data
   
    # Redraw the canvas
    #canvas.draw()

# Create the main application window
#root = tk.Tk()
#root.title("Real-Time 3D Quiver Plot")
#
## Create a Matplotlib figure and axis
#fig = Figure(figsize=(6, 6))
#ax = fig.add_subplot(111, projection='3d')
#
## Create a canvas to embed the Matplotlib figure in the Tkinter window
#canvas = FigureCanvasTkAgg(fig, master=root)
#canvas.get_tk_widget().pack()
#
## Start the Tkinter main loop
#tk.mainloop()
if __name__ == "__main__":
    global orientation_data
    global orientation_data_force

    orientation_data = {"u": 0, "v": 0, "w": 0}
    orientation_data_force = {"x": 0, "y": 0, "z": 0}

    # Create MQTT client
    mqtt_client = mqtt.Client()
    mqtt_force_client = mqtt.Client()
    
    mqtt_client.on_message = on_message
    mqtt_force_client.on_message = on_message_force

    mqtt_client.connect(mqtt_broker_host)
    mqtt_force_client.connect(mqtt_broker_host)

    mqtt_client.subscribe(mqtt_topic)
    mqtt_force_client.subscribe(mqtt_force_topic)

    mqtt_client.loop_start()
    mqtt_force_client.loop_start()

    try:
        while True:
            u = orientation_data["u"]
            v = orientation_data["v"]
            w = orientation_data["w"]
            
            x = orientation_data_force["x"]
            y = orientation_data_force["y"]
            z = orientation_data_force["z"]

            ax.clear()
            ax.quiver(0, 0, 0, u, v, w, color='g', label='Surface Normal')
            ax.quiver(0, 0, 0, x, y, z, color='r', label='Force')

            ax.set_xlabel("X Axis")
            ax.set_ylabel("Y Axis")
            ax.set_zlabel("Z Axis")
            ax.set_xlim(-0.5, 0.5)
            ax.set_ylim(-0.5, 0.5)
            ax.set_zlim(-1, 1)
            ax.legend()

            plt.show(block=False)
            plt.pause(0.01)

         
        
    except KeyboardInterrupt:
        exit()


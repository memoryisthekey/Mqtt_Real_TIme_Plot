import abc
import json
from paho.mqtt import client as mqtt_client
import matplotlib.pyplot as plt
import threading
import matplotlib
import numpy as np
# This line is to avoid screen focus stealing on my pc
matplotlib.use("TkAgg")


# Define a mutex
mutex = threading.Lock()

#todo Improve using singletons?
# Global Variable
data = {"time": []}#, "fx": [], "fy": [], "fz": [], "tx": [], "ty": [], "tz": []}
data3D =[]

# Function that will set the data 
def set_data_structure(format=["fx", "fy", "fz", "tx", "ty", "tz"]):
    if len(format) != len(set(format)):
        raise ValueError("Repeated names are not allowed")
    if format.count("time") > 0:
        raise ValueError("Name \'time\' is not allowed")
    for name in format:
        with mutex:
            data[name] = []
    #print(data)

def set_3Ddata_structure(format=[["x1", "y1", "z1"], ["x2", "y2", "z2"]]):
    for i in range(len(format)):
        if len(format[0][i]) != len(set(format[0][i])):
            raise ValueError("Repeated names are not allowed")
    #print(len(format))
    for i in range(len(format)):
        dictionary = dict()
        for name in format[i]:
            dictionary[name] = []
        data3D.append(dictionary)
    #print(data3D)




class MqttPublisher(abc.ABC):
    """
    Mqtt Template Publisher class. 
    Allow publishing data that will be encoded into json format.
    Should support different sizes of lists

    Args:
        broker      (string): IP of the MQTT broker
        port        (int, optional): Port on which to publish. Default is 1883
        topic       (string): Topic name to publish to
        client_id   (string, optional): Unique identifier of client for MQTT broker. Default is "unique_id_pub"

    Returns:
        void: Publishes data to MQTT broker.
    """
    def __init__(self, topic="default/topic", broker="localhost", port=1883, 
                 client_id ="unique_id_pub"):     
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client_id = client_id
        self.client = mqtt_client.Client(self.client_id)
        self.configure_mqtt_client()

    def configure_mqtt_client(self):
        # client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.connect(self.broker, self.port)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    #@abc.abstractmethod
    def publish_data(self, *data):
        data_encoded =  json.dumps(data)
        result = self.client.publish(self.topic, payload=data_encoded, qos=0, retain=False)
        status = result[0]
        if status == 0:
            print(f"Send `{data_encoded}` to topic `{self.topic}`")
        else:
            print(f"Failed to send message to topic {self.topic}")


class MqttSubcriber(abc.ABC):
    """
    Mqtt Template Subscriber class. 

    Args:
        broker      (string): IP of the MQTT broker
        port        (int, optional): Port on which to publish. Default is 1883
        topic       (string): Topic name to publish to
        client_id   (string, optional): Unique identifier of client for MQTT broker. Default is "unique_id_sub"
        d3          (bool, optional): This flag will tell our subscriber if the data is 3D or 2D. Default False --> 2D
    Returns:
        string: Doens't directly return a value, but will set the values in global "data"
    """
    def __init__(self, topic="default/topic", broker="localhost", port=1883, client_id ="unique_id_sub", d3 = False):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client_id = client_id
        self.client = mqtt_client.Client()
        self.client.on_message = self.on_message
        self.data_holder = []
        self.three_d_flag = d3

        self.subscribe()


    def subscribe(self):
        # Create MQTT client
        self.client.connect(self.broker)
        self.client.subscribe(self.topic)
        self.client.loop_start()

    def on_message(self, client, userdata, message):
        try:

            payload = json.loads(message.payload.decode('utf-8'))
            self.data_holder = payload
            i = 0
            if(not self.three_d_flag):
                with mutex:
                    data["time"].append(len(data["time"]))  # Use the time step as the x-coordinate
                    for value in data:
                        if value != "time":
                            data[value].append(self.data_holder[0][i])
                            i+=1
            else:
                for i in range(len(payload)):
                    with mutex:
                        key_list = list(data3D[i].keys())
                        for name, key in zip(payload[i], key_list):
                            data3D[i][key] = name
                #print(data3D)
            #print("Inside", self.data_holder)
            #print("Received data:", payload)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")


class Plot2D:
    """
    Mqtt Template Subscriber class. 

    Args:
        plot_title      (string, optional): Name for the Plot. Default 'Real-time Plot'
        y_label         (string, optional): Name/Units for the Y-Axis. Default 'Force'
        x_label         (string, optional): Name/Units for the X-Axis. Default 'Time Step'

    Returns:
        void: Plots all passed data on a single graph 
        The legend of the graph will depend on the "keys" you have selected when assigning the set_data_structure

    Obs:
        Less overhead than MultiDynamicPlot2D
    """
    def __init__(self, plot_title = 'Real-time Plot', y_label ='Force' , x_label = 'Time Step'):
        self.x_label = x_label
        self.y_label = y_label
        self.plot_title = plot_title
        self.fig, self.axes = plt.subplots()

    def plot(self):
        if not plt.fignum_exists(self.fig.number):
            exit()
        plt.clf()  # Clear the previous plot    
        # Plot the force and torque data
        with mutex:
            for value in data:
                if value != "time":
                    plt.plot(data["time"], data[value], label=value)

        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        plt.title(self.plot_title)
        plt.legend(loc="upper right")      
        plt.pause(0.01)

class DynamicPlot2D:

    """
    A multi plot dynamic wrapper class for 2D plotting. 

    Args:
        num_subplots    (int, optional):    Name for the Plot. Default 'Real-time Plot'
        subplot_names   (list, optional):   Title for the subplots. Default None ---> 'Subplot i'
                                            The size of the list must be the same as num_plots if not set to Default

        subplot_units   (string or list, optional): Title for the Units of each subplots. Default None ---> 'Unit'
                                            The size of the list must be the same as num_plots if not set to Default
                                            If set to a string the subplots are assumed to all have the same unit

        plot_title      (string, optional): Name for the overall plot figure. Default 'Real-time Plot'

    Returns:
        void: Plots data onto the defined number of subplots
        The data will be evenly distributed among the num_subplots selected. 
        If the number of data variables is not divisible by the number of plots the last plot will have the excess/deficit

        The legend of the graph will depend on the "keys" you have selected when assigning the set_data_structure
    """
    def __init__(self, num_subplots=2, subplot_names = None, subplot_units = None, plot_title='Real-time Plot'):
        self.num_subplots = num_subplots
        self.plot_title = plot_title
        
        self.fig, self.axs = plt.subplots(num_subplots, 1, sharex=True, figsize=(10, 5 * num_subplots))

        self.subplot_names = self.verify_subplot_naming(subplot_names, "Subplot")
        self.subplot_units = self.verify_subplot_naming(subplot_units, "Unit")

        self.split_dict_into_parts = lambda data, num_parts: {k: v for k, v in list(data.items())[1:num_parts + 1]}

        if num_subplots == 1:
            self.axs = [self.axs]  # Ensure axs is a list for single subplot case
        
        if num_subplots > len(list(data.keys())[1:]):
              raise ValueError("There must not be more subplots than variables\nReview your num_subplots or how many variables you have when setting data!")


    def verify_subplot_naming(self, subplot_names, name):
        if(not subplot_names):
            return [f'{name} {i + 1}' for i in range(self.num_subplots)]
        else:   
            if len(subplot_names) == 1:
                return [subplot_names for i in range(self.num_subplots)]
            elif len(subplot_names) != self.num_subplots:
                raise ValueError("The number of subplot names/units and subplots must be equal")
            return subplot_names
    
    
    def split_data(self):  
        """
        This method tries to split data into equal subdictionaries, if it is not possible to be 
        split equally the last subdictionary will have the excess
        """    
        # Extract keys (excluding the first key)
        keys = list(data.keys())[1:]

        # Calculate the number of keys per sub-dict
        keys_per_subdict = len(keys) // self.num_subplots

        # Initialize sub-dictionaries
        self.sub_dicts = [{} for _ in range(self.num_subplots)]

        # Distribute keys to sub-dictionaries
        for i in range(self.num_subplots):
            start_idx = i * keys_per_subdict
            end_idx = start_idx + keys_per_subdict

            if i == self.num_subplots - 1:
                # Assign remaining keys to the last sub-dictionary
                self.sub_dicts[i].update({k: data[k] for k in keys[start_idx:]})
            else:
                self.sub_dicts[i].update({k: data[k] for k in keys[start_idx:end_idx]})
        

    def plot(self):

        """
        This method calls split_data() to divide our global data structure for plotting and then does 1 step for plotting
        Args:
            random_colors   (bool, optional): This flag will enable/disable different colors for each graph. Default False ---> Disabled
        Examples:
            How to use this function with examples.

        """
        if not plt.fignum_exists(self.fig.number):
            exit()

        # Split the Data into sub dicts to plot on each subplot
        self.split_data()
        for i, sub_dict in enumerate(self.sub_dicts,0):
            self.axs[i].clear()  # Clear the previous plot in each subplot
            for key, value in sub_dict.items():
                with mutex:
                    self.axs[i].plot(data["time"], value, label=key)
                

            self.axs[i].set_ylabel(self.subplot_units[i])
            self.axs[i].set_title(self.subplot_names[i])
            self.axs[i].legend(loc="upper right")
        self.axs[i].set_xlabel('Time Step')
        plt.title(self.plot_title)

        plt.pause(0.01)


class Plot3DQuiver:

    def __init__(self, colors=['g', 'r'], labels=['Surface Normal', 'Force'], xlim = 0.5, ylim = 0.5, zlim = 1):
        self.fig, self.axes = plt.subplots(subplot_kw=dict(projection="3d"))
        self.num_quivers = len(data3D)
        #todo: check if colors and labels are the correct size according to the data3D len
        self.colors = colors
        self.labels = labels
        self.x_lim = xlim
        self.y_lim = ylim
        self.z_lim = zlim

   
    def plot(self):
        if not plt.fignum_exists(self.fig.number):
            exit()


        self.axes.clear()
        for i in range(len(data3D)):
            key_list = list(data3D[i].keys())
            self.axes.quiver(0,0,0, data3D[i][key_list[0]], data3D[i][key_list[1]], data3D[i][key_list[2]], color=self.colors[i], label=self.labels[i])

        self.axes.set_xlabel("X Axis")
        self.axes.set_ylabel("Y Axis")
        self.axes.set_zlabel("Z Axis")
        self.axes.set_xlim(-self.x_lim, self.x_lim)
        self.axes.set_ylim(-self.y_lim, self.y_lim)
        self.axes.set_zlim(-self.z_lim, self.z_lim)
        self.axes.legend()

        plt.pause(0.01)
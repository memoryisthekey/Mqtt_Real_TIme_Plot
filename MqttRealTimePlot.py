import abc
import json
from paho.mqtt import client as mqtt_client
import matplotlib.pyplot as plt
import threading
import matplotlib
# This line is to avoid screen focus stealing on my pc
matplotlib.use("TkAgg")


# Define a mutex
mutex = threading.Lock()

data = {"time": []}#, "fx": [], "fy": [], "fz": [], "tx": [], "ty": [], "tz": []}


def set_data_structure(format=["fx", "fy", "fz", "tx", "ty", "tz"]):
    for name in format:
        with mutex:
            data[name] = []
    print(data)



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

    Returns:
        string: Doens't directly return a value, but will set the values in global "data"
    """
    def __init__(self, topic="default/topic", broker="localhost", port=1883, client_id ="unique_id_sub"):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client_id = client_id
        self.client = mqtt_client.Client()
        self.client.on_message = self.on_message
        self.data_holder = []

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
            with mutex:
                data["time"].append(len(data["time"]))  # Use the time step as the x-coordinate
                for value in data:
                    if value != "time":
                        data[value].append(self.data_holder[0][i])
                        i+=1

            #print("Inside", self.data_holder)
            #print("Received data:", payload)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")


class Plot2D():
    def __init__(self, ordered_variables_names = ["fx", "fy", "fz", "tx", "ty", "tz"]):
        self.data_dict = {}
        self.data_dict["time"] = []
        self.ordered_variables_names = ordered_variables_names
        self.data_holder = []
        self.fig, self.axes = plt.subplots(2, 1, sharex=True)
        #self.fig, self.axes = plt.subplots()
        for name in self.ordered_variables_names:
                self.data_dict[name] = list()
    



    def plot(self):
        if not plt.fignum_exists(self.fig.number):
            exit()
        plt.clf()  # Clear the previous plot    
            # Plot the force and torque data
        #plt.subplot(211)
        with mutex:
            for value in data:
                if value != "time":
                    plt.plot(data["time"], data[value], label=value)

        plt.xlabel('Time Step')
        plt.ylabel('Force')
        plt.title('Real-time Force Plot')
        plt.legend()    
        #plt.subplot(212)
        #with mutex:
        #    plt.plot(data["time"], data["tx"], label='Tx')
        #    plt.plot(data["time"], data["ty"], label='Ty')
        ##    plt.plot(data["time"], data["tz"], label='Tz')  
        ##    plt.xlabel('Time Step')
        #plt.ylabel('Torque')
        #plt.title('Real-time Torque Plot')
        #plt.legend()    
        plt.pause(0.01)




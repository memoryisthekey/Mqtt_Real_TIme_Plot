from MqttRealTimePlot import  MqttPublisher, MqttSubcriber, Plot2D
import time
publisher = MqttPublisher("topic")
import numpy as np
time.sleep(2.0)

i =0
j = 0
dt = 0.01  # Time step
frequency = 1.0  # Frequency of the sine wave
amplitude = 1.0 
while(True):
    a = amplitude * np.sin(2 * np.pi * frequency * i * dt)
    b = - amplitude * np.sin(2 * np.pi * frequency * i * dt)

    i +=1
    j -=2
    publisher.publish_data([0, 0,a, b, 0, 0])

    time.sleep(0.05)
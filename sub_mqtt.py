from MqttRealTimePlot import  MqttPublisher, MqttSubcriber, Plot2D
import time
subscriber = MqttSubcriber("topic")
plotter = Plot2D()

try:
    while(True):
        plotter.plot()
except KeyboardInterrupt:
    exit()
from MqttRealTimePlot import  MqttPublisher, MqttSubcriber, Plot2D, set_data_structure
import time

set_data_structure(['x', 'y', 'z'])
subscriber = MqttSubcriber("topic")
plotter = Plot2D()

try:
    while(True):
        plotter.plot()
except KeyboardInterrupt:
    exit()
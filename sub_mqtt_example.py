from MqttRealTimePlot import  MqttPublisher, MqttSubcriber, Plot2D, set_data_structure, DynamicPlot2D
import time

set_data_structure(['fx', 'fy', 'fz', 'tx', 'ty', 'tz'])
subscriber = MqttSubcriber("topic")
plotter = DynamicPlot2D(num_subplots=2, subplot_units='N')

try:
    while(True):
        plotter.plot()
except KeyboardInterrupt:
    exit()
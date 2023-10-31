from MqttRealTimePlot import  MqttPublisher,Plot3DQuiver, MqttSubcriber, Plot2D, set_3Ddata_structure, DynamicPlot2D
import time

set_3Ddata_structure([['fx', 'fy', 'fz'], ['fx', 'fy', 'fz']])
subscriber = MqttSubcriber("topic", d3=True)
plotter = Plot3DQuiver()

try:
    while(True):
        plotter.plot()
except KeyboardInterrupt:
    exit()
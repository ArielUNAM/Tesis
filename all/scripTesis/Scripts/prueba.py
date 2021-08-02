

print(__doc__)


import matplotlib.pyplot as plt
import numpy as np
import pyart
import wradlib

filename = '/home/aceron/Documentos/Radar/CAT150101000114.RAW9HK0'
# create the plot using RadarDisplay (recommended method)
#radar = pyart.io.read_rsl(filename)
radar = pyart.io.read_sigmet(filename)
display = pyart.graph.RadarDisplay(radar)
fig = plt.figure()
ax = fig.add_subplot(111)
display.plot('reflectivity', 0, vmin=-32, vmax=64.)
display.plot_range_rings([10, 20, 30, 40])
display.plot
plt.show()

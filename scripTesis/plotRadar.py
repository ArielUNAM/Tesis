import pyart
import libTesis as lt
import numpy as np
import matplotlib.pyplot as plt

#Rutas a directorios
figp= "/home/arielcg/Documentos/Tesis/imgTesis/"
qro2015= "/home/arielcg/QRO_2015/"
qro2016= "/home/amagaldi/QRO_2016/"
qro2017= "/home/amagaldi/QRO_2017/"

###
#   Formato del archivo 2015
#   RAW_NA_000_236_20150306032609
#   n= 15, antes de llegar a la fecha
#   m= 14 valores despues del _
#                  año|mes|dia|hora

data= lt.getData(qro2015,'RAW_NA_000_236_20150306032609')

#radar = pyart.io.read_sigmet(qro2015+data['07']['01'][0])
radar = pyart.io.read_rsl(qro2015+data['07']['01'][0])
level0=radar.extract_sweeps([0])
acumula= np.load("data/data_07.npz")
level0.add_field('acum', acumula)
display = pyart.graph.RadarDisplay(level0)
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111)
display.plot('acum', 0, title='NEXRAD Reflectivity',  vmin=0, vmax=5, colorbar_label='', ax=ax)
display.plot_range_ring(radar.range['data'][-1]/1000., ax=ax)
display.set_limits(xlim=(-500, 500), ylim=(-500, 500), ax=ax)
plt.savefig("prueba.png")
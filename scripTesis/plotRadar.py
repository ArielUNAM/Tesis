import pyart
import libTesis as lt
import numpy as np
import matplotlib.pyplot as plt
import re, os



#Rutas a directorios
figp= "/home/arielcg/Documentos/Tesis/imgTesis/"
qro2015= "/home/arielcg/QRO_2015/"
qro2016= "/home/amagaldi/QRO_2016/"
qro2017= "/home/amagaldi/QRO_2017/"
datap= "/home/arielcg/Documentos/Tesis/datos/acum/"

###
#   Formato del archivo 2015
#   RAW_NA_000_236_20150306032609
#   n= 15, antes de llegar a la fecha
#   m= 14 valores despues del _
#                  año|mes|dia|hora

data= lt.getData(qro2015,'RAW_NA_000_236_20150306032609')

print("Start to plot")
listData= os.listdir(datap)
r= re.compile("data_03*")
#r= re.compile("RAW_NA*")
for dt in list(filter(r.match,listData)):
    lt.ppi2(datap,dt,qro2015,data['07']['01'][0],dt)
    plt.close()

# idx=['03','04','05','06','07','08','09','10','11','12']
# for id in idx:
#     try:
#         #radar = pyart.io.read_sigmet(qro2015+data['07']['01'][0])
#         radar = pyart.io.read_rsl(qro2015+data['07']['01'][0])
#         level0=radar.extract_sweeps([0])
#         acumula= np.load(datap+"data_{}.npz".format(id))
#         level0.add_field('acum', acumula)
#         display = pyart.graph.RadarDisplay(level0)
#         fig = plt.figure(figsize=(20, 20)) #Relación 1
#         ax = fig.add_subplot(111)
#         display.plot('acum', 0, title='Reflectivity',  vmin=0, vmax=150, colorbar_label='', ax=ax)
#         display.plot_range_ring(radar.range['data'][-1]/1000., ax=ax)
#         display.set_limits(xlim=(-240, 240), ylim=(-240, 240), ax=ax)#Esto es los rangos del radar
#         plt.savefig(figp+"fig{}.png".format(id))
#     except:
#         print("error: ",id)
####################################
# 
#     Ariel Cerón González
#     Intento final para terminar la tesis de licenciatura. 
#     Objetivo: Generar información de precipitación acumulada con 
#               información de datos del radar de Querétaro.
#
#      01 Marzo de 2021
#
#######################################


import libTesis as lt

from operator import mul
import matplotlib.pyplot as plt
import numpy as np
from time import sleep
import re, os
import pickle
#from Tesis.scripTesis.libTesis import *
#import pandas as pd
#from tqdm import tqdm

#Rutas a directorios
figp= "/home/arielcg/Documentos/Tesis/imgTesis/"
qro2015= "/home/arielcg/QRO_2015/"
qro2016= "/home/arielcg/QRO_2016/"
qro2017= "/home/arielcg/QRO_2017/"
datap= "/home/arielcg/Documentos/Tesis/datos/acum/"
###
#   Formato del archivo 2015
#   RAW_NA_000_236_20150306032609
#   n= 15, antes de llegar a la fecha
#   m= 14 valores despues del _
#                  año|mes|dia|hora

data= lt.getData(qro2016,'RAW_NA_000_236_20150306032609')

rd= lt.read('RAW_NA_000_236_20160102063609',qro2016)
n,m= np.shape(rd['data'][1]['sweep_data']['DB_DBZ']['data'])
fig= plt.figure()
dBZ_ord, pia= lt.radarDataProcessingChain(rd)

print("min dBZ_ord: ",np.min(dBZ_ord))
print("max dBZ_ord: ",np.max(dBZ_ord))
lt.ppi(fig,dBZ_ord,figp+'RAW_NA_000_236_20160102063609',vmax=40)
dBZ= dBZ_ord + pia
print("min dBZ: ",np.min(dBZ))
print("max dBZ: ",np.max(dBZ))
fig.clear()
lt.ppi(fig,dBZ,figp+'RAW_NA_000_236_20160102063609'+'1',vmax=40)
print("min pia: ",np.min(pia))
print("max pia: ",np.max(pia))
fig.clear()
lt.ppi(fig,pia,figp+'RAW_NA_000_236_20160102063609'+'2',vmax=40)

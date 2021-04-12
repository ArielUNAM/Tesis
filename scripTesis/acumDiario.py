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
import matplotlib.pyplot as plt
#from Tesis.scripTesis.libTesis import *
#import pandas as pd

#Rutas a directorios
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

#Practica
#Lextura del primer archivo que se enceuntra en el dia 06 del mes 03
rd= lt.read(data['03']['06'][1],qro2015)
#dBZ= lt.radarDataProcessingChain(rd)
dBZ, vel= lt.radarDataProcessingChain(rd)
Zc= lt.dBZ_to_Zc(dBZ,vel)

fig = plt.figure(figsize=(10,8))
lt.plot_ppi(fig,Zc,title="No",xlabel="Easting from radar (km)",ylabel="Northing from radar (km)",cmap="viridis")
###
plt.show()
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


from operator import mul
import libTesis as lt
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
#from Tesis.scripTesis.libTesis import *
#import pandas as pd


#Rutas a directorios
figp= "/home/arielcg/Documentos/Tesis/imgTesis/"
qro2015= "/home/arielcg/QRO_2015/"
qro2016= "/home/amagaldi/QRO_2016/"
qro2017= "/home/amagaldi/QRO_2017/"
datap= "/home/arielcg/Documentos/Tesis/scripTesis/data/"
###
#   Formato del archivo 2015
#   RAW_NA_000_236_20150306032609
#   n= 15, antes de llegar a la fecha
#   m= 14 valores despues del _
#                  año|mes|dia|hora

data= lt.getData(qro2015,'RAW_NA_000_236_20150306032609')

#Practica con un archivo
#Segun https://www.youtube.com/watch?v=Va88O9zV_AA llovio el sabado 11 de abril de 2015
#Acumulación para los meses 7 y 8
meses= ['07']
elev= 1
for mes in meses:
    acumm= 0
    for dia in list(data[mes].keys()):
        #n= len(data[mes][dia])
        n= 40
        acumd= 0
        for i in range(n):#tqdm(range(n)):
            rd= lt.read(data[mes][dia][i],qro2015)
            if (lt.getElev(rd, elev)):
                vel= lt.getVel(rd,0,1)
                dBZ= lt.radarDataProcessingChain(rd)
                V= lt.dBZ_to_V(dBZ,vel,a=74,b=1.6,mult=False)
                acumd+= V
            #np.ma.acumd(values,mask)(?)
            #np.save('file',a.compressed())
        try:
            np.savez_compressed(datap+"data_{}_{}.npz".format(mes,dia),data=acumd.data,mask=acumd.mask)
            acumm+= acumd
            print("Day {} saved".format(dia))
        except:
            print("Error to export data_{}_{}".format(mes,dia))
    try:
        np.savez_compressed(datap+"data_{}.npz".format(mes),data=acumm.data,mask=acumm.mask)
        print("Month {} saved".format(mes))
    except:
        print("Error to export data_{}".format(mes))



    # fig= plt.figure(figsize=(10,8))
    # lt.ppi(fig,acum,title='Acum',xlabel="x",ylabel="y",cmap="viridis")
    # plt.savefig(figp+mes+"_2015_acum.png")
    # plt.close()

#	v,c= np.unique(list(vel.data.flat), return_counts=True)
#	print("Valores\n")
#	print(v)
#	print("Contador\n")
#	print(c)
#	print("Moda: ", v[np.argmax(c)])

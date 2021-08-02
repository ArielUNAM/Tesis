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
import re, os
import pickle
#from Tesis.scripTesis.libTesis import *
#import pandas as pd
from tqdm import tqdm

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
scan_range= [236000,921]
params_vel= [0,1]
params_trans=[74,1.6,True]

#for qro in [qro2015,qro2016,qro2017]:
for qro in tqdm([qro2016,qro2017]):
    data= lt.getData(qro,'RAW_NA_000_236_20150306032609')

    #Practica con un archivo
    #Segun https://www.youtube.com/watch?v=Va88O9zV_AA llovio el sabado 11 de abril de 2015
    #Acumulación para los meses 7 y 8
    #meses= ['07','08']
    meses= list(data.keys())
    elevation= 1

    #RAW_NA_000_236_20150311001109

    for mes in meses:
        #print("mes",mes[:3])
        acumm= 0
        dias= list(data[mes].keys())
        #print("numdias",dias)
        if ( len(dias) > 0 ):
            for dia in dias:
                n= len(data[mes][dia])
                #n= 10
                #print("number",n)
                acumd= 0
                for i in range(n):#tqdm(range(n)):
                    
                    
                    lt.radar2numpy(data[mes][dia][i],qro,elevation,scan_range,params_vel,params_trans)
                    acumd+= V
                            
                    #np.ma.acumd(values,mask)(?)
                    #np.save('file',a.compressed())
                try:
                    
                    np.savez_compressed(datap+"data{}_{}_{}.npz".format(qro[18:22],mes,dia),data=np.nan_to_num(acumd.data),mask=acumd.mask)
                    acumm+= np.nan_to_num(acumd.data)
                    #print("Day {} saved".format(dia))
                except Exception as e:
                    print(e)
                    print("Error to export data_{}_{}_{}".format(qro[18:22],mes,dia))
                    
            try:
                #np.savez_compressed(datap+"data_{}.npz".format(mes),data=acumm.data,mask=acumm.mask)
                np.savez_compressed(datap+"data_{}_{}.npz".format(qro[18:22],mes),data=acumm.data)
                print("Month {} saved".format(mes))
            except Exception as e:
                print(e)
                print("Error to export data_{}_{}".format(qro[18:22],mes))



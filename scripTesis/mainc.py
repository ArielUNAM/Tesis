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
import numpy as np
from tqdm import tqdm
#from Tesis.scripTesis.libTesis import *
#import pandas as pd


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

#Practica con un archivo
#Lextura del primer archivo que se enceuntra en el dia 06 del mes 03
n= len(data['03']['06'])
acum= 0
for i in tqdm(range(10)):
	rd= lt.read(data['03']['06'][i],qro2015)
	vel= lt.vel2bin(rd)
	dBZ= lt.radarDataProcessingChain(rd)
	Zc= lt.dBZ_to_Zc(dBZ,vel)
	acum+= Zc
	fig= plt.figure(figsize=(10,8))
	lt.ppi(fig,Zc,title='No {}'.format(i),xlabel="x",ylabel="y",cmap="viridis")
	plt.savefig("Individual {}".format(i))
	plt.close()

fig= plt.figure(figsize=(10,8))
lt.ppi(fig,acum,title='Acum',xlabel="x",ylabel="y",cmap="viridis")
plt.savefig("Acum.png")
plt.close()

#	v,c= np.unique(list(vel.data.flat), return_counts=True)
#	print("Valores\n")
#	print(v)
#	print("Contador\n")
#	print(c)
#	print("Moda: ", v[np.argmax(c)])
	

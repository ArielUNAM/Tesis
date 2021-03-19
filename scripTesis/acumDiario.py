import os
import wradlib as wl
import numpy as np
import matplotlib.pyplot as plt
#import pandas as pd


#Rutas a directorios
qro2015= "/home/amagaldi/QRO_2015"
qro2016= "/home/amagaldi/QRO_2016"
qro2017= "/home/amagaldi/QRO_2017"

###
#   Formato del archivo 2015
#   RAW_NA_000_236_20150306032609
#   n= 15, antes de llegar a la fecha
#   m= 14 valores despues del _
#                  año|mes|dia|hora

###
# El algoritmo para acumulación diaria contará con cuatro funciones:
#     1. Laprimera generará una lista ordenada de todos los datos para cada directorio
#     2. La segunda generará una lista ordenada de todos los datos correspondientes a un mes
#     3. La tercera generará una lista ordenda de todos los datos correspondientes a un día
#     4. La última generará un archivo que contendrá el acumulado para ese día
#La siguiente parte del código tratará de generar imagenes con la salida de la última función


#Generación de datos ordenados por mes y dia
orderList= sorted(os.listdir(qro2015))

orderDicMon= {'01':[], '02':[], '03':[], '04':[],'05':[], '06':[],
                '07':[], '08':[], '09':[], '10':[],'11':[], '12':[]}
for data in orderList:
    mes= data[19:21]
    orderDicMon[mes].append(data)

orderDicData= {}

for key, values in orderDicMon.items():
    orderDicDay= {}
    for value in values:
        day= value[21:23]
        try:
            orderDicDay[day].append(value)
        except:
            orderDicDay[day] = []
            orderDicDay[day].append(value)
    orderDicData[key]= orderDicDay


    

    





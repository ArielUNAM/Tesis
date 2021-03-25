####################################
# #
#     Ariel Cerón González
#     Intento final para terminar la tesis de licenciatura. 
#     Objetivo: Generar información de precipitación acumulada con información de datos del radar de Querétaro
#       01 Marzo de 2021
###
# El algoritmo para acumulación diaria contará con cuatro funciones:
#     1. La primera generará una lista ordenada de todos los datos para cada directorio
#     2. La segunda generará una lista ordenada de todos los datos correspondientes a un mes
#     3. La tercera generará una lista ordenda de todos los datos correspondientes a un día
#     4. La última generará un archivo que contendrá el acumulado para ese día
#La siguiente parte del código tratará de generar imagenes con la salida de la última función
#######################################

import os
import wradlib as wl
import numpy as np
import matplotlib.pyplot as plt
from libTesis import *
#import pandas as pd


#Rutas a directorios
qro2015= "/home/amagaldi/QRO_2015/"
qro2016= "/home/amagaldi/QRO_2016/"
qro2017= "/home/amagaldi/QRO_2017/"

###
#   Formato del archivo 2015
#   RAW_NA_000_236_20150306032609
#   n= 15, antes de llegar a la fecha
#   m= 14 valores despues del _
#                  año|mes|dia|hora


dicData= getDicData(qro2015,'RAW_NA_000_236_20150306032609')




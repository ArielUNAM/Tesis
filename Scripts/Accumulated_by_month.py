####################################################
#
#           Ariel Cerón González
#           Segundo script para tesis de licenciatura
#           UMDI,       10 de Febrero 2020
#           
#
####################################################


#Para poder user la libreria wradlib es necesario contar con datos contenidos en https://github.com/wradlib/wradlib-data/blob/master/README.md
#Paso siguiente exportarlos.
#bash: export WRADLIB_DATA=/path/to/wradlib-data
#current cmd: set WRADLIB_DATA D:\Users\doop\Documents\VisualCode\Tesis\wradlib_data_master
#code D:\Users\dooph\Anaconda3\envs\wradlib\lib\site-packages\wradlib\util.py
#Modificar la linea 706, habeis añadido un try

######################################Librerias
import glob
import os
import warnings
from datetime import date, timedelta
import pandas as pd

import matplotlib.pyplot as pl
import numpy as np
import wradlib as wrl
import wradlib.georef as georef
import wradlib.io as io
import wradlib.util as util
from scipy import stats
from wradlib.io import *
from wradlib.util import get_wradlib_data_file

warnings.filterwarnings('ignore')

try:
    get_ipython().magic("matplotlib inline")
except:
    pl.ion()



###############################################Funciones
def Lmonth(path:str,year:int, month:int)->list:
    """Regresa una lista ordenada de los nombres de los archivos de radar que se encuentren en un directorio específico y sobre ciertas fechas


    Parameters
    ----------
    path : str
        Ubicación del directorio donde se va a buscar los datos
    year : int
        Año del dato que se quiera obtener
    month : int
        Mes del dato que se quiera obtener

    Returns
    -------
    list    
        Lista ordenada de datos que cumplen con las fechas indicadas. Si no encuentra nada regresa una lista vacia.
    """    
    FIni = date(year,month,1)
    return(sorted(glob.glob(path+"/RAW_NA_000_"+"*"+"_"+str(FIni.year)+'%02d'%FIni.month+"*")))


###############################################Rutas
dirDa = r'D:\\Users\\dooph\\Documents\\VisualCode\\Tesis\\DATA_2015'
##Cambiamos el directorio 
os.chdir(dirDa)

################################################Lectura de datos
AllFilesL = Lmonth(dirDa,2015,3)
print(AllFilesL[:10])
print(len(AllFilesL))

################################################Acumulados
j = 0   #Contador 
dataM = np.zeros((360,921))   #Matriz que guarda los datos

#while not AllFilesL:
for elementos in range(1):
    j += 1  #Contador de elementos
    
    #Iniciamos el tratamiento leyendo cada archivo
    f = wrl.util.get_wradlib_data_file(AllFilesL.pop(0))
    print(f)
    #Evitamos cualquier dato corrupto
    try:
        #Nuestros datos son SIGMET por eso usamos iris
        fcontent = wrl.io.read_iris(f)
        nbins = fcontent['product_hdr']['product_end']['number_bins']
        #Primer dato medido (metros -> km)
        gate_0 = fcontent['ingest_header']['task_configuration']['task_range_info']['range_first_bin']
        #Ultimo dato medido (metros -> km)
        gate_nbin = fcontent['ingest_header']['task_configuration']['task_range_info']['range_last_bin']
        gate_size = round((gate_nbin - gate_0)/(nbins))
        #gate_size = content['ingest_header']['task_configuration']['task_range_info']['step_ouput_bins']
        #Crea una matriz de rangos de exploración
        range_rad = gate_0 + gate_size * np.arange(nbins,dtype='float32')
    except:
        print("Error")
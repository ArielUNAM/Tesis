####################################################
#
#           Ariel Cerón González
#           Primer script para tesis de licenciatura
#           UMDI,       13 de Enero 2020
#           
#
####################################################

#bash: export WRADLIB_DATA=/path/to/wradlib-data
#current cmd: set WRADLIB_DATA D:\Users\doop\Documents\VisualCode\Tesis\wradlib_data_master
#code D:\Users\dooph\Anaconda3\envs\wradlib\lib\site-packages\wradlib\util.py
#Modificar la linea 706, habeis añadido un try

#Librerias
import glob
import os
import wradlib as wrl
import warnings
import matplotlib.pyplot as pl
import numpy as np
from wradlib.util import get_wradlib_data_file
from wradlib.io import *
import wradlib.georef as georef
import wradlib.io as io
import wradlib.util as util
from datetime import date, timedelta

warnings.filterwarnings('ignore')

try:
    get_ipython().magic("matplotlib inline")
except:
    pl.ion()

#Definimos el direcotrio de datos del radar.
#path = r'/home/aceron/Documentos/Radar/RAW_DATA'
#pathImg = r'/home/aceron/Documentos/Radar/Images'
path = r'D:\\Users\\dooph\\Documents\\VisualCode\\Tesis\\RAW_2015'
pathImg = r'D:\\Users\\dooph\\Documents\\VisualCode\\Tesis\\Images'
os.chdir(path)

print("Directory of data:", os.getcwd())

#Definimos las fechas para la lectura de datos
dateS = date(2015, 3, 6)    #Start date
dateE = date(2015, 10, 30)     #End date
delta = dateE - dateS

#Definimos el nombre de los archivos segun la fecha definida
#filename = "/RAW_NA_000_236_2015"+'%02d'%dateS.month+'%02d'%dateS.day+"*"
filename = "/RAW_NA_000_236_2015"+'%02d'%dateS.month+"*"
#filename = "/RAW_NA_000_236_2015"+"*"

allFiles = sorted(glob.glob(path+filename))
#print(len(allFiles), "from",dateS,"to",dateE)
print("All files from ", dateS.year, "number of files: ", len(allFiles))

#Creamos una matriz para guardar el acumulado
dataMatriz = np.zeros((360,921))

i = 0   #Contador
j = 0

#Iniciamos el ciclo que recogera el acumulado
for fname in allFiles:
    #print(fname)
    j += 1
    f = wrl.util.get_wradlib_data_file(fname)   #Set the name 
    #print(f)
    fcontent = wrl.io.read_iris(f)   #Read data from file
    #type(fcontent)
    nbins = fcontent['product_hdr']['product_end']['number_bins']
    #print(nbins)
    gate_0 = fcontent['ingest_header']['task_configuration']['task_range_info']['range_first_bin']/100
    #print(gate_0)
    gate_nbin = fcontent['ingest_header']['task_configuration']['task_range_info']['range_last_bin']/100
    gate_size = round((gate_nbin - gate_0)/(nbins))
    range_rad = gate_0 + gate_size * np.arange(nbins,dtype='float32')
    #Cuando el valor de exploración es 236000 es porque hubo lluvia, que es el momento que nos interesa
    #print("Max value: ",max(range_rad),"Min value: ",min(range_rad))
    #print(range_rad)
    #print(range_rad[-1],range_rad.shape[0])
    print("Restantes: ",len(allFiles)-j)
    #Cuando el valor de exploración es 236000 es porque hubo lluvia, que es el momento que nos interesa
    if range_rad[-1] == 236000.0 and range_rad.shape[0] == 921:
        if fcontent['product_hdr']['product_configuration']['product_specific_info']['sweep_number'] == 1:
            print("Date:",fname[54:58],fname[58:60],fname[60:62],"Time:",fname[62:64],fname[64:66])
            #Datos de la gfecha según su etiqueta en el nombre
            año = fname[54:58]  
            mes = fname[58:60]
            dia = fname[60:62]
            hora = fname[62:64]
            minuto = fname[64:66]
            range_radc_bien = range_rad
            d = fcontent['data'][1]['sweep_data']['DB_DBZ']['data']
            #Limpiamos y filtramos la información
            clutter = wrl.clutter.filter_gabella(d, tr1=12, n_p=6, tr2=1.1)
            data_no_clutter = wrl.ipol.interpolate_polar(d, clutter)
            #pia = wrl.atten.correctAttenuationKraemer(data_no_clutter)
            # pia = wrl.atten.constraint_pia(data_no_clutter)
            pia = wrl.atten.correct_attenuation_constrained(data_no_clutter)
            data_attcorr = data_no_clutter + pia
            Z = wrl.trafo.idecibel(data_attcorr) 
            #R = wrl.zr.z2r(Z, a=220., b=2.0)
            R = wrl.zr.z_to_r(Z,a=220.00,b=2.0)
            #depth = wrl.trafo.r2depth(R, 390)
            depth = wrl.trafo.r_to_depth(R,390)
            Zc = depth*4
            dataMatriz += Zc
            Zc = np.ma.masked_where(Zc < 0.05, Zc)
            cmap = pl.cm.viridis
            cmap.set_bad(color='white')
            ax, cf = wrl.vis.plot_ppi(Zc, cmap="viridis")
            pl.xlabel("Easting from radar (km)")
            pl.ylabel("Northing from radar (km)")
            pl.title("Radar Queretaro"+ u'Precipitación (mm),'+año+"-"+mes+"-"+dia+" "+hora+":"+minuto)
            cb = pl.colorbar(cf, shrink=0.8)
            cb.set_label("mm")
            pl.xlim(-300,300)
            pl.ylim(-300,300)
            pl.grid(color="grey")
            ii = i  
            ii = str(ii)
            pl.savefig(pathImg+ii+'.png')
            print('Imagen guardada')
            i += 1
            pl.close()

dataMatriz = np.ma.masked_where(dataMatriz < 0.05, dataMatriz)
cmap=pl.cm.viridis
cmap.set_bad(color='white')
ax, cf = wrl.vis.plot_ppi(dataMatriz , cmap="viridis")
pl.xlabel("Easting from radar (km)")
pl.ylabel("Northing from radar (km)")
#pl.title("Radar Queretaro"+ u'Precipitación (mm),'+ año +"-"+mes+"-"+dia+" "+hora+":"+minuto)
cb = pl.colorbar(cf, shrink=0.8)
cb.set_label("mm")
pl.xlim(-300,300)
pl.ylim(-300,300)
pl.grid(color="grey")
pl.savefig(path+'acumulacion'+'.png')       

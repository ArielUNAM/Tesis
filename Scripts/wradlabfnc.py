"""
Enero, 2021
Tomado de sat8.py 
"""

import os 
import logging
import wradlib as wl
import warnings
import numpy as np
import matplotlib.pyplot as pl
warnings.filterwarnings('ignore')
try:
    get_ipython().magic("matplotlib inline")
except:
    pl.ion()
    
    
##Funciones
def list_data(path:str,iyear:int,imonth:int,iday:int,fyear:int,fmonth:int,fday:int):
    """
        Función que facilita la lectura en intervalos dados. 
        El archivo esta descrito de la siguiente forma
            
                    CATYYMMDDHHmmSS.EXT
        
    Inputs
    ------
    
    path:str
        Directorio donde se alojan los datos    
    iyear:int
        Año inicial
    imonth:int
        Mes inicial
    iday:
        Día inicial
    fyear:int
        Año final
    fmonth:int
        Mes final
    fday:
        Día final
    
    data:list
        Regresa un arreglo con los nombres de los archivos
    """
    ldata = os.listdir(path)
    iname = "CAT"+str(iyear)[2:]+str(imonth).zfill(2)+str(iday).zfill(2)
    fname = "CAT"+str(fyear)[2:]+str(fmonth).zfill(2)+str(fday).zfill(2)
    filtro = [data for data in ldata if data[:9] in [iname,fname]]
    return(sorted(filtro))


def read_data(path:str,filename:str,elev=None):
    """
        Regresa la lectura de un archivo usando read iris
        
    Inputs
    ------
    path:str
        Ruta del directorio donde se encuentran los datos
    filename:str
        Nombre del archivo a leer
    """
    #to MB
    size = os.stat(path+filename).st_size / (1024 * 1024)
    try:
        if elev == None:
            return(wl.io.iris.read_iris(path+filename))
        else:
            if(getElev(wl.io.iris.read_iris(path+filename),elev)):
                print("siiisisisis")
                return(wl.io.iris.read_iris(path+filename))
            else:
                return((filename,size))
    except:
        return((filename,size))
    
def dBZ_to_Zc(dBZ,vel,a:float = 200,b:float = 1.6,intervalos:int = 390)->list:
    """
        Función auxiliar para obtener datos
    """
    Z = wl.trafo.idecibel(dBZ)
    R = wl.zr.z_to_r(Z,a=a,b=b)
    V = wl.trafo.r_to_depth(R,intervalos)
    return(np.multiply(vel,V))

def preProcess(dBZ):
    """
        Función auxiliar para remover los ruidos, ecos y atenuaciones
    """
    #Desorden (clutter)
    desorden = wl.clutter.filter_gabella(dBZ, tr1=12,n_p=6, tr2=1.1)
    dBZ_ord = wl.ipol.interpolate_polar(dBZ,desorden)
    #Atenuación
    pia_kraemer = wl.atten.correct_attenuation_constrained(
    dBZ_ord,
    a_max=1.67e-4,
    a_min=2.33e-5,
    n_a=100,
    b_max=0.7,
    b_min=0.65,
    n_b=6,
    gate_length=1.,
    constraints=[wl.atten.constraint_dbz],
    constraint_args=[[59.0]])
    return(dBZ_ord + pia_kraemer)
    

def writeLog(txt,typ="warning"):
    if typ not in ["debug","info","warning"]:
        raise Exception("KEYEXCEPTION")    
    else:
        try:
            open("./ariLog.log","r")
        except:
            f = open("./ariLog.log",'w')
            f.close()
            
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s : %(levelname)s : %(message)s',
                    filename = "./ariLog.log",
                    filemode = 'w')
    if typ == "debug":
        logging.debug(txt)
    elif typ == "info":
        logging.info(txt)
    else:
        logging.warning(txt)
        
def add_matrix(matrix,data,i=None):
    """
        Agrega la matriz del acumulado
    """
    if i==1:
        return(data)
    else:
        return(np.append(matrix,data).reshape(i,360,1201))
        
def plot_ppi(fig,acum,title,xlabel,ylabel,cmap):
    
    ax, cf = wl.vis.plot_ppi(acum, cmap=cmap,fig=fig)
    #ax, cf = wl.vis.plot_ppi(acum,fig=fig)
    pl.xlabel(xlabel)
    pl.ylabel(ylabel)
    cb = pl.colorbar(cf, shrink=0.8)
    cb.set_label("mm")
    #pl.xlim(-128,128)
    #pl.ylim(-128,128)
    pl.grid(color="grey")
    
def iris_ver(fcontent):
    try:
        fcontent['product_hdr']['product_end']['iris_version_created']
    except:
        print("Error")
    
def getCoord(fcontent):
    return(fcontent['product_hdr']['product_end']['latitude'],
          fcontent['product_hdr']['product_end']['longitude'])

def getElev(fcontent,elev)->bool:
    print(fcontent['data'][1]['sweep_data']['DB_DBT']['ele_start'].mean())
    print(fcontent['product_hdr']['product_configuration']['product_name'])
    if (fcontent['data'][1]['sweep_data']['DB_DBT']['ele_start'].mean() <  elev):
        return(True)
    else:
        return(False)

def getRange(fcontent,dist,shape):
    nbins=(fcontent['product_hdr']['product_end']['number_bins'])
    gate_0 =(fcontent['ingest_header']['task_configuration']['task_range_info']['range_first_bin']/100)
    gate_nbin =(fcontent['ingest_header']['task_configuration']['task_range_info']['range_last_bin']/100)
    gate_size=round((gate_nbin - gate_0)/(nbins))
    range_rad=gate_0 + gate_size * np.arange(nbins, dtype='float32')
    print(range_rad[-1],range_rad.shape[0])
    if (range_rad[-1] == dist) and (range_rad.shape[0] == shape):
        return(True)
    else:
        return(False)
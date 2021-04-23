################
#   Ariel Cerón G.
#
#   UNAM
#   Queratero, 2021
#   Tesis de licenciatura
#
#   Funciones auxiliares para trabajar con la libreria wradlib
#
########################################################

import os
from collections import OrderedDict
import wradlib as wl
import numpy as np
import matplotlib.pyplot as plt

# Processing functions
#######################
def radarDataProcessingChain(data:OrderedDict, elev:list= [], dist:int= -1, shape: int= -1):
    """ Regresa un archivo dBZ listo para ser usado en alguna aplicación numerica o para graficar 

    Los archivos de radar se encuentran codificados en diferentes formatos, esta es una de las principales limitantes para los usuarios de los radares. wradlib otorga un conjunto de funciones que permiten, leer, filtrar, corregir y presentar de forma gráfica la información contenida en los archivos producidor por un radar. El conjunto de pasos para transformar la información de radar a un formato manipulable es conocido omo "radar data processin chain", estos pasos no son unicos y cada aplicación puede requerir de más o menos pasos, sin embargo podemos destacr:
        1- Lectura
        2- Corrección de desorden
        3- Corrección de la atenuación
        4- Conversión de reflectividad a dBZ (Z to R)
        5- Presentación de los datos
    En esta función nos enfocamos en los puntos 2, 3 y agregamos algunos parámetros utiles para lograr el objetivo de la tesis.
    More info https://docs.wradlib.org/en/1.1.0/notebooks/basics/wradlib_workflow.html

    Parameters
    ----------
    data : OrderedDict
        Por definir
    elev : list
        El usuario puede elegir el rango de elvaciones que mejor le permitan desarrollar la actividad.
    dist : int
        La distancia máxima de exploración tambien puede ser definida, para que todos los datos sea homogoneos en tamaño
    shape : int
        Por definir

    Outputs:
    --------
    dBZ: numpy.narray
        Por deinir 
    """    
    if ( (type(data) != OrderedDict) ):
        raise "File not expected"
    else:
        dBZ= data['data'][1]['sweep_data']['DB_DBZ']['data']
        if ( not elev ):
            pass
        if ( dist == -1 ):
            pass
        if ( shape == -1 ):
            pass

    
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

def vel2bin(data:OrderedDict, val:float=0.0):
	"""
		Transfrorma los valores de velocida a valores 0 y 1
	"""
	vel= data['data'][1]['sweep_data']['DB_VEL']['data']
	vel[vel == 0.0]= val
	vel[vel != 0]= 1
    
	return vel


def dBZ_to_V(dBZ,vel,a:float = 200,b:float = 1.6,intervalos:int = 390,mult=True):
    """ Converting Reflectivity to Rainfall

    Reflectivity (Z) and precipitation rate (R) can be related in form of a power law Z=a⋅Rb. The parameters a and b depend on the type of precipitation

    More info: https://docs.wradlib.org/en/stable/notebooks/basics/wradlib_get_rainfall.html

    Parameters
    ----------
    dBZ : [type]
        [description]
    vel : [type]
        [description]
    a : float, optional
        [description], by default 200
    b : float, optional
        [description], by default 1.6
    intervalos : int, optional
        [description], by default 390

    Returns
    -------
    list
        [description]
    return(np.multiply(vel,V))

    """
    Z = wl.trafo.idecibel(dBZ)
    R = wl.zr.z_to_r(Z,a=a,b=b)
    V = wl.trafo.r_to_depth(R,intervalos)
    if mult:
        return np.multiply(vel,V)
    else:
        return V

def add_matrix(matrix,data,i=None):
    """
        Agrega la matriz del acumulado
    """
    if i==1:
        return(data)
    else:
        return(np.append(matrix,data).reshape(i,360,1201))
        
def ppi(fig,acum,title,xlabel,ylabel,cmap):
    
    ax, cf = wl.vis.plot_ppi(acum, cmap=cmap,fig=fig)
    #ax, cf = wl.vis.plot_ppi(acum,fig=fig)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    cb = plt.colorbar(cf, shrink=0.8)
    cb.set_label("mm")
    #plt.xlim(-128,128)
    #plt.ylim(-128,128)
    plt.grid(color="grey")
    

# Get info functions
####################

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

def getVer(fcontent):
    try:
        fcontent['product_hdr']['product_end']['iris_version_created']
    except:
        raise "Don't found version"

# Get data functions
####################

def getData(path:str,basename:str) -> dict:
    """Devuelve un diccionario del nombre de los archivos

    Dado un path que contiene diversos archivos de radar, regresa un diccionario de dos niveles ordenado de la siguiente forma:
        * Las primeras llaves son un número en el rango [01,12] que representa un mes del año
        * Las segundas llaves son un número en el rango [01,31] que represena un día del mes
    Para realizar el filtro se debe indicar la estructura básica del nombre del archivo, pues la función basa su filtro en que los nombres contienen en sus últimas posiciones la información de fecha.

    Parameters
    ----------
    path : str
        Cadena que contiene la dirección del directorio donde se encuentran los archivos
    basename : str
        Nombre del archivo

    Returns
    -------
    dict
        Directorio de la información obtenida en el directorio dado
    """    
    n= getName(basename)
    
    orderList= sorted(os.listdir(path))
    orderDicMon= dicMonth(orderList,n)

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

    return orderDicData

def dicMonth(orderList:list,n:int)->dict:
    """Regresa un diccionario de datos mensuales

    Parameters
    ----------
    orderList : list
        Lista de nombres ordenada 
    n : int
        Valor inicial de as fechas
    Returns
    -------
    dict
        Diccionario de datos ordenados de forma mensual
    """ 
    orderDicMon= {'01':[], '02':[], '03':[], '04':[],'05':[], '06':[],
                    '07':[], '08':[], '09':[], '10':[],'11':[], '12':[]}

    for data in orderList:
        mes= data[n+4:n+6]
        orderDicMon[mes].append(data)
    return orderDicMon

def getName(basename:str)->int:
    """Regresa la posición inicial de la fecha según el nombre dado

    Parameters
    ----------
    basename : str
        Nombre base de los archivos que serán identificados

    Returns
    -------
    int
        Posición inicial de las fechas en el archivo
    """    
    if basename[:15] == 'RAW_NA_000_236_':
        return 15
    else:
        return 0

def read(filename:str,path:str= 'default'):
    """ Lee un archivo de radar tipo IRIS.

    Tiene como entrada la lectura de un archivo existente en el path para después usando las funciones de lectura de archivos IRIS que tienen la libreria wradlib, regresa un objeto radar (o diccionario) que continen toda la información del archivo leido.

    Es recomendable usar antes la función getData(path,basename) y reciclar la varaible path.

    Parameters
    ----------
    filenae : str
        Nombre del archivo que será leido    
    path : str, optional
        Ruta donde se encuentren los archivos de no definir una entrada se tomara el directorio de trabajo, by default 'default'

    Outputs
    -------
    OrderDict:
        Un diccionario ordenado que contiene toda la información generada por el radar en un cierto intervalo de tiempo.
    """    
    if ( path== 'default' ):
        path= os.getcwd()
    #sizeof= os.stat(path+filename).st_size / (1024 * 1024)
    return wl.io.iris.read_iris(path+filename)

# Debugg functions
##################
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
        

################
#
#   name: pyRadar.py
#   auhor:  Ariel Cerón G.
#   UNAM, Tesis de licenciatura
#   Queratero, 2021
#   
#
#   Entre los datos más codiciados se encuentran la evolución en el tiempo
#   y la distribución espacial de la precipitación pluvial. El radar 
#   meteorológico es un instrumento de observación atmosférica orientado a
#   la vigilancia continua (en tiempo y espacio) de la precipitación   
#   pluvial. Uno de los usos es la itensidad de lluvia instantanea en mm/h
#   que produce una tormenta una vez ubicada y suponiendo que se 
#   encontrara suficientemente cerca (a unos 230 km). Es importante 
#   puntualizar que no se trata de una estimación cualitativa sino de  
#   una medición que, bajo una calibración cuidadosa, sirva para 
#   establecer las tasas de precipitación con errores de más menos veinte
#   por ciento. Algunos radares pueden también indicar el tipo de lluvia,
#   sin embargo esto aún debe considerarse como en etapa de desarrollo.
#   
#   Un radar emite un pulso electromagnético a una cierta frecuencia, 
#   cuando este pulso choca con algún objeto se produce una disipación de 
#   la energía hacia todas direcciones y parte de esta energía es devuelta 
#   al radar. La potencia que el radar capta en distintos instantes se 
#   corresponde a la energía devuelta por diferentes volúmenes situados a 
#   lo largo del eje del haz y a distancia creciente de este. El 
#   procedimiento de emisión-escucha se repite para cada dirección radial 
#   en la que se realiza un muestreo. De esta forma, fijado un cierto 
#   ángulo de la antena respecto a la horizontal, usualmente llamado 
#   elevación, el radar efectúa un barrido de la atmósfera girando 360 
#   grados y realizando un número determinado de muestreos radiales.
#
#   El conjunto de medidas realizado por el radar son usualmente 
#   integradas en programas que permiten de forma interactiva consultar en 
#   tiempo real los datos que el radar está recogiendo y manipularlos. 
#   Muchos de los programas existentes tienen limitaciones o no son 
#   programas de acceso público. Sin embargo existen proyectos de código 
#   libre implementadas en python que intentan generar herramientas para 
#   manipular información proveniente de diferentes marcas de radares 
#   meteorológicos entre ellos se encuentra wradlib y pyart.
#
#   Las funciones implementadas en este archvio intentan aprovechar las 
#   herramientas de código libre para obtener informació sobre la 
#   evolución temporal y espacial de la precipitación pluvial ocurrida en 
#   el estado de Querétaro y adquirida por el radar ubicado en el cerro de 
#   la Ronchera. 
#
#   ======================================================================
#
#   Sientanse libres de usar las funciones que más le sirva y si es de su 
#   interes aumentar las funciones o mejorar las cadenas de procesamiento 
#   es bienvenida su aporte al código, clone y cree una nueva rama del 
#   proyecto indicando en esta sección un resumen de lo que fue agregado, 
#   para revisar e integrar el el código principal.
#
#   ======================================================================
#
#   Fuentes de Consulta:
#   * Moshinsky, M. R. (1995). Fundamentos de radares meteorológicos:
#   aspectos clásicos (primera de dos partes). Tecnología y ciencias
#   del agua, 10(1), 55-74.
#   * Heistermann, M., Jacobi, S., and Pfaff, T.: Technical Note: An open 
#   source library for processing weather radar data (wradlib), Hydrol. 
#   Earth Syst. Sci., 17, 863-871, doi:10.5194/hess-17-863-2013, 2013
#   * Helmus, J.J. & Collis, S.M., (2016). The Python ARM Radar Toolkit 
#   (Py-ART), a Library for Working with Weather Radar Data in the Python 
#   Programming Language. Journal of Open Research Software. 4(1), p.e25. 
#   DOI: http://doi.org/10.5334/jors.119
#
########################################################

# Radar libraries
# ================
import itertools
from tkinter import Y
from wradlib.util import get_wradlib_data_file
import wradlib as wl
import pyart
import wradlib.vis as vis
import wradlib.util as util
import osgeo as osr

# Data processing libraries
# ================
import numpy as np
import numpy.ma as ma
from collections import OrderedDict
import datetime
import pandas as pd
import re

# Graphical libraries
# ==================
import matplotlib.pyplot as plt
from pyproj import CRS
from pyproj import Transformer  
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib import cm

# System libraries
# =================
import os

# Warnigs
# =================
import warnings
warnings.filterwarnings('ignore')
try:
    get_ipython().magic("matplotlib inline")
except:
    plt.ion()


# VARIABLES
# =================
MONTHS_LIST= ['01','02','03','04','05','06','07','08','09','10','11','12']
SCANN_RANGE= [236000,921]
PARAM_VEL= [0,1]
PARAM_TRANS=[74,1.6,True]
ELEVATION= 1
FILEBASE= '/home/arielcg/Documentos/Tesis/src/data/base/geoBase.csv'
CMAP= 'GnBu'

# Acquisition and ordering
# ========================================
def get_path_files(root_of_dirs:str, rex:str)->list:
    """Returns a list of paths located at the root and matching the regular expression. I suppose that your files are organizated in folders.

    :param root: Path of the directory files
    :type root: str
    :param re: Regular expression of folder or files
    :type rex: str
    :return: List of paths located at the root and matching the regular expression
    :rtype: list
    """
    return [root_of_dirs + string for string in os.listdir(root_of_dirs) if re.match(rex,string)]

def get_files_from_path(path_to_data:str)->dict:
    """Returns a dictionary of dictionaries that stores the location of the data classified by month and day. This info is the key

    :param path_to_data: Path of the data 
    :type path_to_data: str
    :return: A dictionary of dictionaries of data radar
    :rtype: dict
    """
    orderList= sorted( os.listdir( path_to_data ) )
    n= get_word_length_until(orderList[0],'_')
    orderDicMon= get_dict_of_data_by_month(orderList,n)


    orderDicData= {}

    for month, values in orderDicMon.items():
        orderDicDay= {}
        for value in values:
            day= value[21:23]
            try:
                orderDicDay[day].append(path_to_data + '/' + value)
            except:
                orderDicDay[day] = []
                orderDicDay[day].append(path_to_data + '/' + value)
        orderDicData[month]= orderDicDay

    return orderDicData

def get_dict_of_data_by_month(ldata:list,date_len:int)->dict:
    """Return a dict of data sorted by months

    :param ldata: List of radar data names
    :type ldata: list
    :param date_len: Length of date info
    :type date_len: int
    :return: A dict of data sorted by months
    :rtype: dict
    """
    orderDicMon= {'01':[], '02':[], '03':[], '04':[],'05':[], '06':[],
                    '07':[], '08':[], '09':[], '10':[],'11':[], '12':[]}

    for data in ldata:
        mes= data[date_len+4:date_len+6]
        orderDicMon[mes].append(data)
    return orderDicMon

def get_word_length_until(word:str,symbol:str,inverse:bool=True)->int:
    """Return the length of a word until a defined symbol appears

    :param word: Word to measure
    :type word: str
    :param symbol: Symbol to stop the measure
    :type symbol: str
    :return: The length of a word until a defined symbol appears
    :rtype: int
    """
    ini= 0
    fin= len(word)
    pas= 1

    if( inverse ):
        ini= len(word) - 1
        fin= 0
        pas= -1

    for i in range(ini,fin,pas):
        if( word[i] == symbol ):
            return i + 1
        continue

# Data reading and processing Wradlib
# ========================================
def est_rain_rate_z(path_to_data:str,pia_type:str='default',tr1:float=12,n_p:float=12,tr2:float=1.1,a:float = 200,b:float = 1.6,intervalos:int = 390,mult=True,bool_vel:bool= True,angle:float=1)->tuple:
    """Return the acum from a file

    :param path_to_data: Path to file data
    :type path_to_data: str
    :param pia_type: Attenuation correction, defaults to 'default'
    :type pia_type: str, optional
    :param tr1: _description_, defaults to 12
    :type tr1: float, optional
    :param n_p: _description_, defaults to 12
    :type n_p: float, optional
    :param tr2: _description_, defaults to 1.1
    :type tr2: float, optional
    :param a: _description_, defaults to 200
    :type a: float, optional
    :param b: _description_, defaults to 1.6
    :type b: float, optional
    :param intervalos: _description_, defaults to 390
    :type intervalos: int, optional
    :param mult: _description_, defaults to True
    :type mult: bool, optional
    :param bool_vel: _description_, defaults to True
    :type bool_vel: bool, optional
    :param angle: _description_, defaults to 1
    :type angle: float, optional
    :return: _description_
    :rtype: _type_
    """
    iris_data= get_iris_data( path_to_data )

    if( get_elevation(iris_data,True) < angle ):
        
        dBZ, pia= data_processing_chain(iris_data,pia_type,tr1,n_p,tr2,)
        velocity= get_velocity(iris_data,bool_vel)

        return np.shape(velocity), reflectivity_to_rainfall(dBZ+pia,velocity,a,b,intervalos,mult)

    return False, False

def reflectivity_to_rainfall(dBZ:np.ndarray,vel:np.ndarray,a:float = 200,b:float = 1.6,intervalos:int = 390,mult=True, zeros:bool=True)->np.ndarray:
    """Converting Reflectivity to Rainfall

    Reflectivity (Z) and precipitation rate (R) can be related in form of a power law Z=a⋅Rb. The parameters a and b depend on the type of precipitation

    More info: https://docs.wradlib.org/en/stable/notebooks/basics/wradlib_get_rainfall.html

    :param dBZ: [description]
    :type dBZ: ndarray
    :param vel: [description]
    :type vel: [type]
    :param a: [description], defaults to 200
    :type a: float, optional
    :param b: [description], defaults to 1.6
    :type b: float, optional
    :param intervalos: [description], defaults to 390
    :type intervalos: int, optional
    :param mult: [description], defaults to True
    :type mult: bool, optional
    :return: [description]
    :rtype: ndarray
    """
    Z = wl.trafo.idecibel(dBZ)
    R = wl.zr.z_to_r(Z,a=a,b=b)
    depth = wl.trafo.r_to_depth(R,intervalos)

    if mult:
        vel=data_cleaner(vel)
        depth= np.multiply(vel,depth)

    if( zeros ):
        return np.where(depth < 0,0 ,depth )

    return depth

def data_processing_chain(iris_data:OrderedDict,pia_type:str='default',tr1:float=12,n_p:float=12,tr2:float=1.1)->tuple:
    """Return a tuple of data after a processed

    In order to use weather radar observations for quantitative studies he data has to be carefully processed in order to account for typical errors sources such as ground echoes (clutter), attenuation of the radar signal, or uncertainties in the Z/R relationship.
    Read more: https://docs.wradlib.org/en/1.1.0/notebooks/basics/wradlib_workflow.html

    :param iris_data: A iris data after read by wradlib
    :type iris_data: OrderedDict
    :param pia_type: Type of pia processing
    :type pia_type: str
    :return: A tuple of data after a processed
    :rtype: tuple
    """
    reflectivity= get_reflectivity(iris_data)
    reflectivity= data_cleaner(reflectivity)
    
    dBZ_ord = clutter_processing(reflectivity,
                                         tr1=tr1,n_p=n_p, tr2=tr2)

    if ( pia_type == 'default' ):
        pia= pia_processing(dBZ_ord)
    else:
        pia= pia_processing(dBZ_ord,
            a_max=1.67e-4,
            a_min=2.33e-5, 
            n_a=100,
            b_max=0.7,
            b_min=0.65,
            n_b=6, 
            gate_length=1.,
            constraints= [wl.atten.constraint_dbz,wl.atten.constraint_pia],
            constraint_args=[[59.0],[20.0]])

    pia= data_cleaner(pia)
    return (dBZ_ord,pia)

def get_clutter(reflectivity:np.ndarray,wsize:int=5,thrsnorain:int=0,tr1:float=12,n_p:float=12,tr2:float=1.1,clutter:bool=True)->np.ndarray:
    """ Return a np.ndarray after a clutter filter

    Clutter filter published by Gabella et al., 2002 is applied

    :param reflectivity: [description]
    :type reflectivity: np.ndarray
    :param tr1: [description], defaults to 12
    :type tr1: float, optional
    :param n_p: [description], defaults to 12
    :type n_p: float, optional
    :param tr2: [description], defaults to 1.1
    :type tr2: float, optional
    :return: [description]
    :rtype: [type]
    """
    if( clutter ):
        return wl.clutter.filter_gabella(reflectivity,wsize=wsize,thrsnorain=thrsnorain,tr1=tr1,n_p=n_p, tr2=tr2)
    else:
        return wl.clutter.histo_cut(reflectivity)
                                
def clutter_processing(reflectivity:np.ndarray,wsize:int=5,thrsnorain:int=0,tr1:float=12,n_p:float=12,tr2:float=1.1)->np.ndarray:
    """ Return a np.ndarray after a clutter filter

    Clutter filter published by Gabella et al., 2002 is applied

    :param reflectivity: [description]
    :type reflectivity: np.ndarray
    :param tr1: [description], defaults to 12
    :type tr1: float, optional
    :param n_p: [description], defaults to 12
    :type n_p: float, optional
    :param tr2: [description], defaults to 1.1
    :type tr2: float, optional
    :return: [description]
    :rtype: [type]
    """

    return wl.ipol.interpolate_polar(reflectivity,get_clutter(reflectivity,wsize=wsize,thrsnorain=thrsnorain,tr1=tr1,n_p=n_p, tr2=tr2))

def pia_processing(dBZ_order:np.ndarray,a_max:float=1.67e-4,
                        a_min:float=2.33e-5,
                        n_a:float=100,
                        b_max:float=0.7,
                        b_min:float=0.65,
                        n_b:float=6,
                        gate_length:float=1,
                        constraints:list=[wl.atten.constraint_dbz],
                        constraint_args:list=[[59.0]])->np.ndarray:
    """Return values to correct the reflectivity values

    :param dBZ_order: Reflectivity after clutter
    :type dBZ_order: np.ndarray
    :param a_max: [description], defaults to 1.67e-4
    :type a_max: float, optional
    :param a_min: [description], defaults to 2.33e-5
    :type a_min: float, optional
    :param n_a: [description], defaults to 100
    :type n_a: float, optional
    :param b_max: [description], defaults to 0.7
    :type b_max: float, optional
    :param b_min: [description], defaults to 0.65
    :type b_min: float, optional
    :param n_b: [description], defaults to 6
    :type n_b: float, optional
    :param gate_length: [description], defaults to 1
    :type gate_length: float, optional
    :param constraints: [description], defaults to [wl.atten.constraint_dbz]
    :type constraints: list, optional
    :param constraint_args: [description], defaults to [[59.0]]
    :type constraint_args: list, optional
    :return: [description]
    :rtype: np.ndarray
    """
    return wl.atten.correct_attenuation_constrained(
        dBZ_order,
        a_max=a_max,
        a_min=a_min,
        n_a=n_a,
        b_max=b_max,
        b_min=b_min,
        n_b=n_b,
        gate_length=gate_length,
        constraints=constraints,
        constraint_args=constraint_args)
        
def data_cleaner(data:np.ndarray,nan:float=0,posinf:float=0,neginf:float=0)->np.ndarray:
    """Return a np.ndarray change the nan an inf values

    :param data: Numpy array of data
    :type data: np.ndarray
    :param nan: Values to nan, defaults to 0
    :type nan: float, optional
    :param posinf: Values to -inf, defaults to 0
    :type posinf: float, optional
    :param neginf: Values to +inf, defaults to 0
    :type neginf: float, optional
    :return: A np.ndarray change the nan an inf values
    :rtype: np.ndarray
    """
    return np.nan_to_num(data, copy=False, nan=nan, posinf=posinf, neginf=neginf)

def get_range(iris_data:OrderedDict) ->float:
    """Return the pulse radius

    :param iris_data: Iris data
    :type iris_data: OrderedDict
    :return: Pulse radius
    :rtype: float
    """
    nbins=(iris_data['product_hdr']['product_end']['number_bins'])
    gate_0 =(iris_data['ingest_header']['task_configuration']['task_range_info']['range_first_bin']/100)
    gate_nbin =(iris_data['ingest_header']['task_configuration']['task_range_info']['range_last_bin']/100)
    gate_size=round((gate_nbin - gate_0)/(nbins))
    return gate_0 + gate_size * np.arange(nbins, dtype='float64')

def get_version(iris_data:OrderedDict)->str:
    """Retur the versión of iris

    :param iris_data: Iris object
    :type iris_data: OrderedDict
    :return: Iris version
    :rtype: str
    """
    return iris_data['product_hdr']['product_end']['iris_version_created']

def get_elevation(iris_data:OrderedDict,prom=False)->np.ndarray:
    """Return the elevation value

    :param iris_data: Iris Objecto
    :type iris_data: OrderedDict
    :return: Elevation value
    :rtype: np.ndarray
    """
    arry= iris_data['data'][1]['sweep_data']['DB_DBT']['ele_start'].copy()
    if( prom ):
        return np.mean(arry)
    return arry

def get_velocity(iris_data:OrderedDict, unmmasked:bool= True)->np.ndarray:
    """Return the velocity of a iris data.

    :param iris_data: [description]
    :type iris_data: OrderedDict
    :param maskedVal: [description], defaults to None
    :type maskedVal: float, optional
    :param unmmaskedVal: [description], defaults to None
    :type unmmaskedVal: float, optional
    :param processing: [description], defaults to False
    :type processing: bool, optional
    :return: [description]
    :rtype: np.ndarray
    """

    vel= iris_data['data'][1]['sweep_data']['DB_VEL']['data'].filled().copy() if unmmasked else iris_data['data'][1]['sweep_data']['DB_VEL']['data'].copy()

    return vel

def get_azimuth(iris_data:OrderedDict, start:bool=True)->np.ndarray:
    """Return the iris azimuth 
    
    El azimut es el ángulo que forma el Norte y un cuerpo celeste, medido en sentido de rotación de las agujas de un reloj alrededor del horizonte del observador.

    :param iris_data: [description]
    :type iris_data: OrderedDict
    :return: [description]
    :rtype: np.ndarray
    """
    str_az= 'azi_start' if start else 'azi_stop'
    
    return iris_data['data'][1]['sweep_data']['DB_DBT'][str_az].copy()

def get_reflectivity(iris_data:OrderedDict)->np.ndarray:
    """Return the reflectivity of a iris data.

    Precipitation intensity is measured by a ground-based radar that bounces radar waves off of precipitation. The Local Radar base reflectivity product is a display of echo intensity (reflectivity) measured in dBZ (decibels).


    :param iris_data: [description]
    :type iris_data: OrderedDict
    """
    return iris_data['data'][1]['sweep_data']['DB_DBZ']['data'].copy()

def get_coordinates(iris_data:OrderedDict,minusRotate:bool=False,getHeigth:bool=False)->tuple:
    """Return the lon and lat of a iris data

    :param iris_data: [description]
    :type iris_data: OrderedDict
    :return: [description]
    :rtype: tuple
    """
    if (minusRotate):
        if ( getHeigth ):
            h= iris_data['product_hdr']['product_end']['ground_height'] + iris_data['product_hdr']['product_end']['radar_height']
            return(iris_data['product_hdr']['product_end']['longitude']-360,
                   iris_data['product_hdr']['product_end']['latitude'],
                   h)
        else:
            return(iris_data['product_hdr']['product_end']['longitude']-360,
                   iris_data['product_hdr']['product_end']['latitude'])
    else:
        if ( getHeigth ):
            h= iris_data['product_hdr']['product_end']['ground_height'] + iris_data['product_hdr']['product_end']['radar_height']
            return(iris_data['product_hdr']['product_end']['longitude'],
                   iris_data['product_hdr']['product_end']['latitude'],
                   h)
        else:
            return(iris_data['product_hdr']['product_end']['longitude'],
                   iris_data['product_hdr']['product_end']['latitude'])

def get_iris_data(path_iris:str)->dict:
    """Return an wradlib file type of iris file

    :param path_iris: Path to iris file
    :type path_iris: str
    :return: Dictionary with data and metadata retrieved from file.
    :rtype: OrderedDict
    """
    return wl.io.iris.read_iris(path_iris)

def get_radar(path_radar:str)->pyart.core.radar.Radar:
    """[summary]

    :param path_radar: [description]
    :type path_radar: str
    :return: [description]
    :rtype: pyart.core.radar.Radar
    """
    try:
        return pyart.io.read_sigmet(path_radar)
    except:
        return pyart.io.read(path_radar)

def get_mask_from_data( data:np.arange )->np.ma.array:
    """Return a masket data array for better presentation

    :param data: Data to assing mask
    :type data: np.arange
    :return: A maskedArray
    :rtype: np.ma.array
    """
    maks_ind= np.where( data <= np.nanmin( data ) )
    data[ maks_ind ]= np.nan
    return np.ma.array( data, mask= np.isnan( data ) )

def get_metadata( iris_data:OrderedDict )->tuple:
    return get_range( iris_data ), get_azimuth( iris_data ), get_coordinates( iris_data )

# Automatic processing
# ========================================
def get_list_dir(path:str,isDir=True)->list:
    """Return a list whit all directories in the path. If false then retun all files that are'nt a directory

    :param path: Path where realize the searh
    :type path: str
    :param isDir: If true find directories else files, defaults to True
    :type isDir: bool, optional
    :return: A list of directories names or files names
    :rtype: list
    """
    list_names= os.listdir(path)
    if ( isDir ):
        return [name for name in list_names if os.path.isdir(name)]
    else:
        return [name for name in list_names if not os.path.isdir(name)]
    
def mkdir(path:str,name:str):
    """Make a directory on the indicated path with the indicated name

    :param path: Path where the direct gona make
    :type path: str
    :param name: Dir name
    :type name: str
    """
    list_dir= get_list_dir(path)
    if ( name not in list_dir ):
        os.mkdir(path+name)

def int_to_str(number:int)->str:
    """Return a str type number

    :param number: A number
    :type number: int
    :return: A number
    :rtype: str
    """
    if ( number < 9 ):
        return '0'+str(number)
    else:
        return str(number)

def generate_directory_structure(dict_of_data_path:dict,year:str,path:str):
    """In a specific directory path generate a directory estrucuture in base a directory strucutrure like 

        /path
        |-/year
        |   |-/month
        |   |   |-/week
        |   |   |   |-numpyfile

    :param dict_of_data_path: A dicrectory strucuture
    :type dict_of_data_path: dict
    :param year: A year
    :type year: str
    :param path: A path
    :type path: str
    """
    mkdir(path,year)
    path= path+year+'/'
    months= dict_of_data_path.keys()
    for month in months:
        if ( dict_of_data_path[month] ):
            mkdir(path,month)
        days= dict_of_data_path[month].keys()
        if ( days ):
            for day in days:
                n_week= int_to_str(get_week_number(year,month,day))
                mkdir(path+month+'/',n_week)

def get_week_number(year:str,month:str,day:str)-> int:
    """Return the number of a week

    :param year: A year
    :type year: str
    :param month: A month
    :type month: str
    :param day: A day
    :type day: str
    :return: Number of week
    :rtype: int
    """
    return datetime.date(int(year), int(month), int(day)).isocalendar()[1]

def generate_daily_acum(path_to_data:str,dict_of_data:dict,path_to_save:str,year:str,month:str,day:str):
    """Realize the daily sum of data radar (located in path to data) and save in path_to_save in a npz format

    :param path_to_data: Data located
    :type path_to_data: str
    :param dict_of_data: A file structure dict
    :type dict_of_data: dict
    :param path_to_save: Path to save acum data
    :type path_to_save: str
    :param year: A year
    :type year: str
    :param month: A month
    :type month: str
    :param day: A day
    :type day: str
    """
    days= dict_of_data[month].keys()
    acum= 0
    if ( days ):
        data= dict_of_data[month][day]
        if ( data ):
            for d in data:
                iris= get_iris_data(path_to_data+d)
                dBZ,pia= data_processing_chain(iris)
                acum+= reflectivity_to_rainfall(dBZ+pia,
                                    get_velocity(iris),mult=False)
            n_week= int_to_str(get_week_number(year,month,day))
            path_to_save= path_to_save+year+'/'+month+'/'+n_week+'/'
            np.savez_compressed(path_to_save+"/radar_{}_{}_{}.npz".format(year,month,day),data=acum,coords=get_coordinates(iris),range=get_range(iris))

def acum_daily(path2root:str,path2save:str,dict2data:dict):
    """Generate a daily acumalted from 

    :param path2root: [description]
    :type path2root: str
    :param path2save: [description]
    :type path2save: str
    :param dict2data: [description]
    :type dict2data: dict
    """
    for year, path in dict2data.items():
        dic_of_data= get_files_from_path(path2root+path)
        generate_directory_structure(dic_of_data,year,path2save)
        for month in dic_of_data.keys():
        #for month in tqdm(months):
            days= dic_of_data[month].keys()
            if ( days ):
                for day in days:
                    generate_daily_acum(path2root+path,dic_of_data,path2save,year,month,day)

def acum_by_path(path2list:str)->np.ndarray:
    """Return a numpy.ndarray of the acum data

    :param path2list: Path where the npz data are
    :type path2list: str
    :return: A numpy.ndarray
    :rtype: np.ndarray
    """
    acum= 0
    if ( os.path.isdir(path2list) ):
        data= get_list_dir(path2list,False)
        if ( data ):
            for dt in data:
                acum+= np.load(path2list + dt)['data']
            return acum

def acum_week(path2save:str,year:str,month:str='',week:str=''):
    """Generate a week acumated

    :param path2save: [description]
    :type path2save: str
    :param year: [description]
    :type year: str
    :param month: [description], defaults to ''
    :type month: str, optional
    :param week: [description], defaults to ''
    :type week: str, optional
    """
    path= path2save+year+'/'
    if not bool(month):
        months= sorted(os.listdir(path))
        if not bool(week):
            weeks=[]
            aux_week= ''
            for month in months:
                path_month= path+month+'/'
                weeks= sorted(os.listdir(path_month))
                for week in weeks:
                    if ( aux_week == week ):
                        path_week= path_month+week+'/'
                        acum_week+= acum_by_path(path_week)
                        aux_week= week
                        np.savez_compressed(path_month+"/radar_{}_{}_{}.npz".format(year,month,week),data=acum_week)
                    else:
                        if bool(aux_week):
                            np.savez_compressed(path_month+"/radar_{}_{}_{}.npz".format(year,month,aux_week),data=acum_week)
                        path_week= path_month+week+'/'
                        acum_week= acum_by_path(path_week)
                        aux_week= week
                np.savez_compressed(path_month+"/radar_{}_{}_{}.npz".format(year,month,week),data=acum_week)
        else:
            data= []
            acum_week=0
            for month in months:
                path_month= path+month+'/'
                weeks= os.listdir(path_month) 
                if ( week in weeks ):
                    path_week= path_month+week+'/'
                    data.append(path_week)
                for dt in data:    
                    acum_week+= acum_by_path(dt)
                np.savez_compressed(path_week+"/radar_{}_{}_{}.npz".format(year,month,week),data=acum_week)
    else:
        if not bool(week):
            aux_week= ''
            path_month= path+month+'/'
            weeks= sorted(os.listdir(path_month))
            for week in weeks:
                if ( aux_week == week ):
                    path_week= path_month+week+'/'
                    acum_week+= acum_by_path(path_week)
                    aux_week= week
                    np.savez_compressed(path_month+"/radar_{}_{}_{}.npz".format(year,month,week),data=acum_week)
                else:
                    if bool(aux_week):
                        np.savez_compressed(path_month+"/radar_{}_{}_{}.npz".format(year,month,aux_week),data=acum_week)
                    path_week= path_month+week+'/'
                    acum_week= acum_by_path(path_week)
                    aux_week= week
            np.savez_compressed(path_month+"/radar_{}_{}_{}.npz".format(year,month,week),data=acum_week)
        else:
            path_month= path+month+'/'
            weeks= os.listdir(path_month) 
            if ( week in weeks ):
                path_week= path_month+week+'/'
                acum_week= acum_by_path(path_week)
                np.savez_compressed(path_month+"/radar_{}_{}_{}.npz".format(year,month,week),data=acum_week)

def acum_month(path2save:str,year:str,month:str=''):
    path= path2save+year+'/'
    months= sorted(os.listdir(path))
    months= [month for month in months if os.path.isdir(path+month)]
    for month in months:
        acum_month= 0
        path_month= path+month+'/'
        weeks= get_list_dir(path_month)
        for week in weeks:
            path_week= path_month+week+'/'
            acum_month+= acum_by_path(path_week)
        np.savez_compressed(path+"/radar_{}_{}.npz".format(year,month),data=acum_month)

def acum_year(path2save:str,year:str=''):
    if ( year ):
        acum_year=0 
        path_year= path2save+year+'/'
        acum_year= acum_by_path(path_year)
        np.savez_compressed(path2save+"/radar_{}.npz".format(year),data=acum_month)

    else:
        years= get_list_dir(path2save)
        for year in years:
            acum_year=0 
            path_year= path2save+year+'/'
            acum_year= acum_by_path(path_year)
            np.savez_compressed(path2save+"/radar_{}.npz".format(year),data=acum_month)

def radar_acum_year(path_to_data:str,path_to_save:str,year:str,month:str='',radar_base:str=''):
    #Obtenemos la información ordenada en un diccionario
    dict_of_data= get_dict_of_data_path( path_to_data )
    radar_base= radar_base if radar_base else  "/home/arielcg/QRO_2016/RAW_NA_000_236_20160729020609" 
    
    #Empezamos el acumulado
    #Acumulado mensual
    for key_month in dict_of_data:
        print(key_month)
        #Acumulado semanal
        radar= get_radar( radar_base )     
        month_acum= None
        for key_day in dict_of_data[key_month]:
            print(key_day)
            day_acum= None
            #Acumulado diario
            for path_day in dict_of_data[key_month][key_day]:
                print(path_day)
                rainfall= est_rain_rate_z( path_to_data + path_day ) 
                day_acum += rainfall
                print(rainfall)
            dict_axu= radar.fields['reflectivity'].copy()
            dict_axu.pop('_FillValue')
            dict_axu['data']= day_acum
            print(day_acum)
            radar.add_field('day_{}'.format(key_day),dict_axu,replace_existing=True)
            month_acum+= day_acum
            print(month_acum)
        if( month_acum ):
            dict_axu= radar.fields['reflectivity'].copy()
            dict_axu.pop('_FillValue')
            dict_axu['data']= month_acum
            print(month_acum)
            print(dict_axu)
            radar.add_field('reflectivity',dict_axu,replace_existing=True)
            pyart.io.write_cfradial(path_to_save+'QRO_{}_{}.nc',format(year,key_month), radar)
                   
def get_acum_by_path(path2data:str,files:list,shape:tuple)->np.ndarray:
    acum= np.zeros(shape, dtype=np.float64)
    for file in files[:3]:
        rain= est_rain_rate_z( path2data + file)
        acum+= rain

    return acum

def clear_radar(radar:pyart.core.radar.Radar)->pyart.core.radar.Radar:
    """Return a radar without fields

    :param radar: A base radar with fields
    :type radar: pyart.core.radar.Radar
    :return: A base radar witout fields
    :rtype: pyart.core.radar.Radar
    """
    keys= radar.fields.copy().keys()
    for key in keys:
        radar.fields.pop( key )
    return radar

def set_radar(path_to_file:str,path_to_save:str,dic,name):
    radar= get_radar(path_to_file)
    
    keys= radar.fields.copy()
    keys= keys.keys()
    for key in keys:
        radar.fields.pop(key)
    
    for key, value in dic.items():
        radar.add_field(key,value,replace_existing=True)
    
    pyart.io.write_cfradial(path_to_save+name+'.nc', radar)

def add_field_to_radar(base_radar:str,field:dict,name:str,radar=None)->pyart:
    """[summary]

    :param base_radar: [description]
    :type base_radar: str
    :param field: [description]
    :type field: dict
    :param name: [description]
    :type name: str
    :param radar: [description], defaults to None
    :type radar: [type], optional
    :return: [description]
    :rtype: pyart
    """
    if( radar is None):
        radar= get_radar(base_radar)

        keys= radar.fields.copy().keys()
        for key in keys:
            radar.fields.pop(key)
    
    radar.add_field( name, field,replace_existing=True)
    #pyart.io.write_cfradial(path_to_save+name+'.nc',radar)
    return radar

def numpy_to_dict(data:np.array,long_name:str, short_name='equivalent_reflectivity_factor',units='dBZ')->dict:
    """Return a base dict that can be added to radar file

    :param data: Matrix data
    :type data: np.array
    :param long_name: Name of the data to add
    :type long_name: str
    :return: A base dict
    :rtype: dict
    """
    return {'units':units,
          'standard_name': short_name,
          'long_name':long_name,
          'coordinates': 'elevation azimuth range',
          'data':data }

def get_acum_by_dict_radar(dic):
    acum= 0
    for key in dic.keys():
        acum+= dic[key]['data']

    print('acum')
    return acum

def get_acum_by_list(path_to_files:list,base_radar:str, angle:float=1)->tuple:
    """Return the acum of a list of radar data whit a given angle

    :param path_to_files: Path to radar file
    :type path_to_files: list
    :param angle: Angle of radar in the scatter, defaults to 1
    :type angle: float, optional
    :return: Acum info of radar data list
    :rtype: tuple
    """
    
    
    radar= get_radar( base_radar )
    acum= np.zeros( ( radar.nrays, radar.ngates), dtype=np.float64 )

    for _file in path_to_files:
        acum+= est_rain_rate_z( _file, angle=angle )

    return acum

    
## Plotting
## ========================================
def __plot_reflectivity(data, title, filename, fig ):
    
    projection = ccrs.LambertConformal(central_latitude=data.latitude['data'][0], central_longitude=data.longitude['data'][0])

    ax = fig.add_subplot(1,1,1, projection=projection)
    lat_0= data.latitude['data'][0]
    lon_0= data.longitude['data'][0]

    display= pyart.graph.RadarMapDisplay( data )
    display.plot_ppi_map('reflectivity',0,
                #width=100, height=100,
                lat_0=lat_0,
                lon_0=lon_0,
                resolution='10m',
                vmin=0,
                projection=projection,
                fig=fig, ax=ax,
                #title=title,
                cmap=cm.get_cmap(CMAP)
                )
    
    plt.savefig(filename)

def plot_reflectivity(data, title:str, bar_label:str='', filename:str='plot_func', radarFrom:bool=False)->None:
    """Save a tipycal reflectivity plot from 
    https://docs.wradlib.org/en/stable/notebooks/fileio/wradlib_load_rainbow_example.html?highlight=reflectivity

    :param data: Numpy matrix of data to plot
    :type data: np.arange
    :param title: Title of the plot
    :type title: str
    :param bar_label: Name at bar
    :type bar_label: str
    :param filename: Name of plot, defaults to 'plot_func'
    :type filename: str, optional

    >>> iris= get_iris_data( filename )
    >>> reflectivity= get_reflectivity( iris )
    >>> plot_reflectivity( reflectivity, 'Titulo', 'Etiqueta', 'Filename')
    >>> radar= get_radar( filename )
    >>> plot_reflectivity( radar , 'Titulo', 'Filename', radarFrom= True)

    """
    fig= plt.figure(figsize=(10,6))
    if( radarFrom ):
        return __plot_reflectivity(data, title, filename, fig )
    
    ma= get_mask_from_data( data )

    ax, pm = wl.vis.plot_ppi(ma, fig=fig, proj='cg',cmap=CMAP)#cmap='winter')
    caax = ax.parasites[0]
    paax = ax.parasites[1]
    ax.parasites[1].set_aspect('equal')

    plt.title(title, y=1.08)
    cbar = plt.gcf().colorbar(pm, pad=0.075, ax=paax, )
    caax.set_xlabel('Rango [km]')
    caax.set_ylabel('Rango [km]')
    plt.text(1.0, 1.05, 'azimuth', transform=caax.transAxes, va='bottom', ha='right')
    cbar.set_label(bar_label)
    
    plt.savefig(filename)

def plot_clutter( data, suptitle:str, filename:str,data_title:str="Datos con desorden",clutter_title:str= "Filtro Gabella", xlabel:str="Rango [km]", ylabel:str="Rango [km]", clmap=None )->None:
    """Plot two graphs, the first one is the reflectivity data, and the second one is the result afther apply a gabella filter

    :param data: Raw data
    :type data: np.array
    :param suptitle: Title of the plot
    :type suptitle: str
    :param filename: Name of the file
    :type filename: str
    :param data_title: Title of the raw data, defaults to "Datos con desorden"
    :type data_title: str, optional
    :param clutter_title: Title of the clutter filter, defaults to "Filtro Gabella"
    :type clutter_title: str, optional
    :param xlabel: Label from the X-axis , defaults to "Rango [km]"
    :type xlabel: str, optional
    :param ylabel: Label from the Y-axis, defaults to "Rango [km]"
    :type ylabel: str, optional
    :param clmap: Can use other clutter filters and pass the result, defaults to None
    :type clmap: _type_, optional

    >>> iris= get_iris_data( filename )
    >>> reflectivity= get_reflectivity( iris )
    >>> plot_clutter( reflectivity, "Filtro Gabella para disminuir el ruido", "gabellaWL")

    """
    
    fig= plt.figure(figsize=(10,6))

    #Fist figure
    #Reflectivity
    ax= fig.add_subplot(121) 
    ma= get_mask_from_data( data )
    ax, pm= wl.vis.plot_ppi( ma, ax=ax, cmap=CMAP)
    ax.set_title( data_title, y=1.05)

    plt.grid(True)

    #Second plot
    #Gabella clutter
    ax= fig.add_subplot(122) 
    if( clmap is None ):
        clmap= wl.clutter.filter_gabella( data, 
                            wsize= 5, thrsnorain=0.,
                            tr1=6., tr2=1.3,
                            n_p=8.)
    ax, pm= wl.vis.plot_ppi( clmap, ax=ax, cmap='GnBu_r' )
    ax.set_title(clutter_title,y=1.05)

    plt.grid(True)

    #Set labels and titles
    plt.suptitle( suptitle, y=0.92)
    fig.text(0.5, 0.15, xlabel, ha='center')
    fig.text(0.04, 0.5, ylabel, va='center', rotation='vertical')

    plt.savefig( filename )

def __plot_beam(radar, beam, title, filename, fig):
    beam= [-102.9,19.9]
    projection = ccrs.LambertConformal(central_latitude=radar.latitude['data'][0], central_longitude=radar.longitude['data'][0])

    ax = fig.add_subplot(1,1,1, projection=projection)
    lat_0= radar.latitude['data'][0]
    lon_0= radar.longitude['data'][0]

    display= pyart.graph.RadarMapDisplay( radar )
    ax= display.plot_ppi_map( 'reflectivity', 0,
                lat_0=lat_0,
                lon_0=lon_0,
                resolution='10m',
                vmin=0,
                projection=projection,
                fig=fig, ax=ax,
                #title=title,
                cmap=cm.get_cmap(CMAP))

    display.plot_line_geo([lon_0,beam[0]],[lat_0,beam], color='black')
    plt.savefig(filename)

def plot_beam( data, beam, title, bar_label, filename, xlabel="Rango [km]", ylabel="Rango [km]", radarFrom=False ):
    """Plot a beam

    :param data: _description_
    :type data: _type_
    :param beam: _description_
    :type beam: _type_
    :param title: _description_
    :type title: _type_
    :param bar_label: _description_
    :type bar_label: _type_
    :param filename: _description_
    :type filename: _type_
    :param xlabel: _description_, defaults to "Rango [km]"
    :type xlabel: str, optional
    :param ylabel: _description_, defaults to "Rango [km]"
    :type ylabel: str, optional
    :param radarFrom: _description_, defaults to False
    :type radarFrom: bool, optional
    :return: _description_
    :rtype: _type_
    """
    fig= plt.figure(figsize=(10,6))
    if( radarFrom ):
        return __plot_beam(data,beam,title,filename,fig)
    ax, cf= wl.vis.plot_ppi( data, cmap=CMAP)

    plt.plot(beam[0],beam[1],"-", color="black", lw=2)
    plt.title( title, y=1.02)
    plt.xlabel( xlabel ); plt.ylabel( ylabel )
    plt.grid(color="grey")

    cb= plt.colorbar( cf, shrink=0.8)
    cb.set_label( bar_label )

    plt.savefig(filename)
                
def plot_beams(data, mybeams, fig, filename, sub=111,title='Attenuation correction 2'):
    ax = fig.add_subplot(sub)
    labelsize=13
    for beam in range(mybeams.start, mybeams.stop):
        plt.plot(data[beam], label="{0} deg".format(beam))
    plt.grid()
    plt.text(0.99, 0.88, "Reflectivity along beams",
            horizontalalignment='right',
            transform = ax.transAxes, fontsize="large")
    #plt.xlabel("range (km)", fontsize="large")
    plt.ylabel("Reflectivity (dBZ)", fontsize="large")
    plt.legend(loc="upper left")
    ax.tick_params(axis='x', labelsize=labelsize)
    ax.tick_params(axis='y', labelsize=labelsize)
    plt.xlim(0,128)
    plt.savefig(filename)

def plot_pia(pia,fig, filename, sub=111, title=None, ylim=30):
    ax = fig.add_subplot(sub)
    labelsize=13
    
    plt.plot(pia.T)
    plt.grid()
    plt.ylim(0,ylim)
    plt.ylabel("PIA (dB)", fontsize="large")
    plt.xlabel("range (km)", fontsize="large")
    plt.text(0.01, 0.88, title,
            transform = ax.transAxes, fontsize="large")
    ax.tick_params(axis='x', labelsize=labelsize)
    ax.tick_params(axis='y', labelsize=labelsize)
    plt.xlim(0,128)
    
    plt.tight_layout()
    plt.savefig(filename)

def __get_att_hb( data ):
    return wl.atten.correct_attenuation_hb( data,
    coefficients = dict(a=200, b=1.6, gate_length=1.0),
    mode="warn",thrs=59. )

def __get_att_hr( data ):
    pia_harrison= wl.atten.correct_attenuation_hb( data,
    coefficients = dict(a=200, b=1.6, gate_length=1.0),
    mode="warn",thrs=59.)
    pia_harrison[pia_harrison > 4.8] = 4.8
    return pia_harrison

def __get_att_kr( data ):
    return wl.atten.correct_attenuation_constrained( data,
    a_max=1.67e-4, a_min=2.33e-5, 
    n_a=100, b_max=0.7, b_min=0.65, 
    n_b=6, gate_length=1.,
    constraints=[wl.atten.constraint_dbz],
    constraint_args=[[59.0]])

def __get_att_mk( data ):
    return wl.atten.correct_attenuation_constrained( data,
    a_max=1.67e-4, a_min=2.33e-5,
    n_a=100, b_max=0.7,
    b_min=0.65, n_b=6,
    gate_length=1.,
    constraints=[wl.atten.constraint_dbz,
                 wl.atten.constraint_pia],
    constraint_args=[[59.0],[20.0]])

def plot_attenuation( data, beams, filename:str, ylim=30,pia_title:str="PIA according to Kraemer", beams_title:str="PIA according to Kraemer", type:str="kraemer"):
    """Plot two figures

    :param data: Raw data
    :type data: np.arange
    :param beams: Angles
    :type beams: Tuple
    :param filename: Name of the files
    :type filename: str
    :param ylim: Limits to pia plot, defaults to 30
    :type ylim: int, optional
    :param pia_title: Name of pia plot, defaults to "PIA according to Kraemer"
    :type pia_title: str, optional
    :param beams_title: Name of bemas plot, defaults to "PIA according to Kraemer"
    :type beams_title: str, optional
    :param type: Select the pia filtrer, defaults to "kraemer"
    :type type: str, optional
    :raises ValueError: Return the type of filtred select

    >>> iris= get_iris_data( filename )
    >>> reflectivity= get_reflectivity( iris )
    >>> mybeams= slice(250, 255) 
    >>> plot_attenuation( reflectivity, mybeams, filename )
    """
    fig= plt.figure( figsize=(10,6) )
    fig.tight_layout() 
    
    if( type.__eq__( "kraemer" ) ):
        pia= __get_att_kr( data )
    elif( type.__eq__( "harrison" ) ):
        pia= __get_att_hr( data )
    elif( type.__eq__( "mkraemer" ) ):
        pia= __get_att_mk( data )
    elif( type.__eq__( "hitchfeld" ) ):
        pia= __get_att_hb( data )
    else:
        raise ValueError( f"Pia {type} don't found")
    plot_beams(data, beams, fig, filename, 211, pia_title)
    plot_pia(pia[beams],fig, filename, 212, beams_title, ylim=ylim)

## Others
## ========================================

def get_project_trasnform(file:str,epsg:int)->tuple:
    """Return the lon and lat transformation of a file to as pesg

    :param file: path of the file
    :type file: str
    :param epsg: id of epsg
    :type epsg: int
    :return: A tupple of list
    :rtype: tuple
    """
    crs= CRS.from_epsg(epsg)
    proj= Transformer.from_crs(crs.geodetic_crs,crs)
    df= pd.read_csv(file)
    lat=[]
    lon=[]

    for i in range(df.shape[0]):
        LAT,LON= proj.transform(df.Latitude[i],df.Longitude[i]) 
        lat.append(LAT)
        lon.append(LON)

    return np.array(lon),np.array(lat)

def get_middle_points(X:list, Y:list)->tuple:
    
    new_X= []
    new_Y= []
    for i in range(1, len( X ) ):
        x= ( X[i - 1] + X[i] ) / 2
        y= ( Y[i - 1] + Y[i] ) / 2
        new_X.append( x )
        new_Y.append( y )
    return list(itertools.product(new_X,new_Y))

    #Inteta obtener la mitad de la linea y luego la mitad de la linea y luego haces pares para que obtengas los medios 
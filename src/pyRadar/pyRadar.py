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
from genericpath import isdir
import itertools
import wradlib as wl
import pyart

# Data processing libraries
# ================
import numpy as np
from collections import OrderedDict
import datetime
import pandas as pd
import re
from math import isnan, isinf

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
# try:
#     get_ipython().magic("matplotlib inline")
# except:
#     plt.ion()


# VARIABLES
# =================
MONTHS_LIST= ['01','02','03','04','05','06','07','08','09','10','11','12']
SCANN_RANGE= [236000,921]
PARAM_VEL= [0,1]
PARAM_TRANS=[74,1.6,True]
ELEVATION= 1
FILEBASE= '/home/arielcg/Documentos/Tesis/src/data/base/geoBase.csv'
CMAP= 'GnBu'


# CONFIG
# =================
params = {'axes.labelsize': 15,
          'axes.titlesize': 20}
plt.rcParams.update(params)

# Acquisition and ordering
# ========================================
def get_path_files(root_of_dirs:str, rex:str, is_dir:bool=True)->list:
    """Returns a list of paths located at the root and matching the regular expression. I suppose that your files are organizated in folders.

    :param root: Path of the directory files
    :type root: str
    :param re: Regular expression of folder or files
    :type rex: str
    :return: List of paths located at the root and matching the regular expression
    :rtype: list
    """
    if is_dir:
        return [root_of_dirs + string for string in os.listdir(root_of_dirs) if re.match(rex,string) and isdir(root_of_dirs + string)]
    else:
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

# Data reading and processing 
# ========================================
def get_iris(path_iris:str)->dict:
    """Return an wradlib file type of iris file

    :param path_iris: Path to iris file
    :type path_iris: str
    :return: Dictionary with data and metadata retrieved from file.
    :rtype: OrderedDict
    """
    return wl.io.iris.read_iris(path_iris)

def get_radar(path_radar:str)->pyart.core.radar.Radar:
    """Return a radar object from a radar file

    :param path_radar: Path of the radar file
    :type path_radar: str
    :return: A radar object
    :rtype: pyart.core.radar.Radar
    """
    try:
        return pyart.io.read_sigmet(path_radar)
    except:
        return pyart.io.read(path_radar)

def est_rain_rate_z(path_to_data:str,pia_type:str='default',tr1:float=12,n_p:float=12,tr2:float=1.1,a:float = 200,b:float = 1.6,intervalos:int = 390,mult=True,bool_vel:bool= True,angle:float=1)->np.arange:
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
    iris_data= get_iris( path_to_data )

    if( get_elevation(iris_data, True) < angle ):
        
        dBZ, pia= data_processing_chain(iris_data,pia_type,tr1,n_p,tr2,)
        velocity= get_velocity(iris_data, bool_vel)

        return reflectivity_to_rainfall( dBZ+pia,velocity, a ,b ,intervalos, mult )

    return 

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
    Z = wl.trafo.idecibel( dBZ )
    R = wl.zr.z_to_r( Z, a=a, b=b )
    depth = wl.trafo.r_to_depth( R, intervalos )

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
    #reflectivity= data_cleaner(reflectivity)
    
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

    #pia= data_cleaner(pia)
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

def get_shape( iris:OrderedDict )->tuple:
    return get_reflectivity( iris ).shape
# Data processing
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

def get_radar_acum( radar:pyart.core.radar.Radar, fields:list=None ):
    if fields is None :
        fields= [ field.replace(' ','') for field in 
                    radar.metadata['field_names'].split(',') ]
    acum= np.zeros((radar.nrays,radar.ngates))

    for field in fields:
        acum+= radar.fields[ field ][ 'data' ].filled()

    return acum

def get_acum( files:list,a:float = 200,b:float = 1.6 )->np.array:
    acum= np.zeros( ( get_shape( get_iris( files[0] ) ) ) )
    for file in files:
        try:
            acum+= data_cleaner(  est_rain_rate_z( file, a=a, b=b ) )
        except:
            print(est_rain_rate_z( file, a=a, b=b ))
    return acum


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

def numpy_to_radar_dict(data:np.array,long_name:str, short_name='equivalent_reflectivity_factor',units='dBZ')->dict:
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
def get_coords( radar:pyart.core.radar.Radar )->tuple:
    """Return a tuple of coordinates from radar basis 

    :param radar: A radar object
    :type radar: pyart.core.radar.Radar
    :return: A tuple of lon and lat from radar basis
    :rtype: tuple
    """
    return radar.longitude['data'][0], radar.latitude['data'][0]

## Plotting
## ========================================
def __axis_config(ax):
    ax.set_aspect("equal")
    #ax.add_feature(cfeature.COASTLINE)
    # ax.add_feature(cfeature.OCEAN, facecolor='#CCFEFF')
    # ax.add_feature(cfeature.LAKES, facecolor='#CCFEFF')
    # ax.add_feature(cfeature.RIVERS, edgecolor='#CCFEFF')
    # ax.add_feature(cfeature.LAND, facecolor='#FFE9B5')
    # ax.add_feature(cfeature.STATES, edgecolor='black', zorder=10)

def __plot_reflectivity(data, title, filename, fig, vmax=45):
    
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
                vmin=0,vmax=vmax,
                projection=projection,
                fig=fig, ax=ax,
                #title=title,
                cmap=cm.get_cmap(CMAP)
                )
    __axis_config( ax )
    
    
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

    >>> iris= get_iris( filename )
    >>> reflectivity= get_reflectivity( iris )
    >>> plot_reflectivity( reflectivity, 'Titulo', 'Etiqueta', 'Filename')
    >>> radar= get_radar( filename )
    >>> plot_reflectivity( radar , 'Titulo', 'Filename', radarFrom= True)

    """
    fig= plt.figure(figsize=(10,7))
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

    >>> iris= get_iris( filename )
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
    ax, pm= wl.vis.plot_ppi( clmap, ax=ax, cmap=plt.cm.gray)#cmap='GnBu_r' )
    ax.set_title(clutter_title,y=1.05)

    __axis_config( ax )

    plt.grid(True)

    #Set labels and titles
    plt.suptitle( suptitle, y=0.98, fontsize=30)
    fig.text(0.5, 0.1, xlabel, ha='center')
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
    # ax.xaxis.label.set_size(50)

    __axis_config( ax )

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

    __axis_config( ax )

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
    """Plot two figuresincl

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

    >>> iris= get_iris( filename )
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

def plot_labels( display:pyart.graph.RadarMapDisplay, labels:list, coords:list ):
    """Plot a list of labels into a given a RadarMapDisplay at the coords

    :param display: A RadarMapDisplay where the data ll'be display
    :type display: pyart.graph.RadarMapDisplay
    :param labels: A list of elements asociate a coord position
    :type labels: list
    :param coords: Coordinates positions
    :type coords: list
    """
    for coor, label in zip( coords, labels ):
        display.plot_point( coor[0], coor[1], 'None', label_text=label, label_offset=(-0.01,0))

def plot_point( display:pyart.graph.RadarMapDisplay,  coords:list ):
    """Plot points into a RadarMaDisplay at the coords

    :param display: A RadarMapDisplay where the data ll'be display
    :type display: pyart.graph.RadarMapDisplay
    :param coords: Coordinates position
    :type coords: list
    """
    for coor in coords:
        display.plot_point( coor[0], coor[1], label_offset=(-0.01,0))

# def plot_labels_from_file( display:pyart.graph.RadarMapDisplay,  filename, name ):
#     df= pd.read_csv( filename )
#     for _, coord in df[['Latitude','Longitude']].iterrows():
#         display.plot_point(coord[1], coord[0], 'None',label_text=name, color='r', label_offset=(-0.01,0))

def plot_field( radar:pyart.core.radar.Radar, field:str, display:pyart.graph.RadarMapDisplay,  fig, projection,title:str, filename:str, vmin= 0, vmax= 200):
    """Plot the ppi representation from a radar object and the given field

    :param radar: A pyart radar object
    :type radar: pyart.core.radar.Radar
    :param field: Name of the radar that ll'be plot
    :type field: str
    :param display: A RadarMapDisplay where the figure ll'be plot
    :type display: pyart.graph.RadarMapDisplay
    :param fig: A matplotlib figure
    :type fig: _type_
    :param projection: _description_
    :type projection: _type_
    :param title: Title of plot
    :type title: str
    :param filename: Name of the figure generated
    :type filename: str
    :param vmin: Minimum value represented, defaults to 0
    :type vmin: int, optional
    :param vmax: Maximum value represented, defaults to 200
    :type vmax: int, optional
    """
    #Figure
    ax= fig.add_subplot( 1,1,1, projection= projection )

    #Radar coords
    lon_0, lat_0= get_coords( radar )

    #Plotting
    display.plot_ppi_map( field,
                          lat_0= lat_0,
                          lon_0= lon_0,
                          resolution= '10m',
                          vmin= vmin, vmax= vmax,
                          projection= projection,
                          fig= fig, ax= ax,
                          title= title,
                          cmap= cm.get_cmap('GnBu')
                        )
    display.plot_point(lon_0, lat_0,label_text='Radar')

    #Axis
    ax.xaxis.set_tick_params(rotation=35)
    ax.set_aspect("equal")
    # ax.xaxis.label.set_size(50)
    

    #savefig
    plt.savefig( filename )

def plot_field_section( radar:pyart.core.radar.Radar, field:str, display:pyart.graph.RadarMapDisplay,  fig, projection,title:str, filename:str, lat_max:float= 19.8, lat_min:float= 21.7,lon_max:float= -100.59, lon_min:float= -99.0, n_blocks:int= 15, vmin:int= 0, vmax:int= 200, savefig=True):
    """Plot a section at a radar

    :param radar: _description_
    :type radar: pyart.core.radar.Radar
    :param field: _description_
    :type field: str
    :param display: _description_
    :type display: pyart.graph.RadarMapDisplay
    :param fig: _description_
    :type fig: _type_
    :param projection: _description_
    :type projection: _type_
    :param title: _description_
    :type title: str
    :param filename: _description_
    :type filename: str
    :param lat_max: _description_, defaults to 19.8
    :type lat_max: float, optional
    :param lat_min: _description_, defaults to 21.7
    :type lat_min: float, optional
    :param lon_max: _description_, defaults to -100.59
    :type lon_max: float, optional
    :param lon_min: _description_, defaults to -99.0
    :type lon_min: float, optional
    :param n_blocks: _description_, defaults to 10
    :type n_blocks: int, optional
    :param vmin: _description_, defaults to 0
    :type vmin: int, optional
    :param vmax: _description_, defaults to 200
    :type vmax: int, optional
    """
    #Figure
    ax= fig.add_subplot( 1,1,1, projection= projection )

    #Radar coords
    lon_0, lat_0= get_coords( radar )

    #Lines
    lat_lines=np.linspace(lat_min, lat_max, n_blocks)
    lon_lines=np.linspace(lon_min, lon_max, n_blocks)

    #Plotting
    display.plot_ppi_map( field,
                          lat_0= lat_0,
                          lon_0= lon_0,
                          max_lat=lat_max, min_lat=lat_min,
                          max_lon=lon_max, min_lon=lon_min,
                          lat_lines= lat_lines,
                          lon_lines= lon_lines,
                          resolution= '10m',
                          vmin= vmin, vmax= vmax,
                          projection= projection,
                          fig= fig, ax= ax,
                          title= title,
                          cmap= cm.get_cmap('GnBu'),
                          #colorbar_flag=False
                        )
    display.plot_point(lon_0, lat_0,label_text='Radar')

    #Axis
    ax.xaxis.set_tick_params(rotation=35)
    ax.set_aspect("equal")
    # ax.xaxis.label.set_size(50)

    #savefig
    if savefig:
        plt.savefig( filename )

def plot_field_points_section( radar, field:str, display:pyart.graph.RadarMapDisplay,  fig, projection,title:str, filename:str, lat_max:float= 19.8, lat_min:float= 21.7,lon_max:float= -100.59, lon_min:float= -99.0, n_blocks:int= 15, vmin:int= 0, vmax:int= 200, middle_points:bool=True):
    #Figure
    ax= fig.add_subplot( 1,1,1, projection= projection )

    #Radar coords
    lon_0, lat_0= get_coords( radar )

    #Lines
    lat_lines=np.linspace(lat_min, lat_max, n_blocks)
    lon_lines=np.linspace(lon_min, lon_max, n_blocks)

    #Plotting
    display.plot_ppi_map( field,
                          lat_0= lat_0,
                          lon_0= lon_0,
                          max_lat=lat_max, min_lat=lat_min,
                          max_lon=lon_max, min_lon=lon_min,
                          lat_lines= lat_lines,
                          lon_lines= lon_lines,
                          resolution= '10m',
                          vmin= vmin, vmax= vmax,
                          projection= projection,
                          fig= fig, ax= ax,
                          title= title,
                          cmap= cm.get_cmap('GnBu'),
                          #colorbar_flag=False
                        )
    display.plot_point(lon_0, lat_0,label_text='Radar')

    #Axis
    ax.xaxis.set_tick_params(rotation=35)
    ax.set_aspect("equal")
    # ax.xaxis.label.set_size(50)

    if( middle_points ):
        mp= get_middle_points( lon_lines, lat_lines )
        plot_point( display, mp )

    #savefig
    plt.savefig( filename )

def plot_field_labels_acum_section( radar, field:str, display:pyart.graph.RadarMapDisplay,  fig, projection,title:str, filename:str, lat_max:float= 19.8, lat_min:float= 21.7,lon_max:float= -100.59, lon_min:float= -99.0, n_blocks:int= 15, vmin:int= 0, vmax:int= 200, middle_points:bool=True, max_val:float=10000,nnear=1):
    #Zeros field
    radar.add_field( 'ZEROS', numpy_to_radar_dict(
        np.zeros((360,921)),
        'Acumulado anual 2015',
        'ACUM ANUAL',
        'mm'),  replace_existing=True)

    #Figure
    ax= fig.add_subplot( 1,1,1, projection= projection )

    #Radar coords
    lon_0, lat_0= get_coords( radar )

    #Lines
    lat_lines=np.linspace(lat_min, lat_max, n_blocks)
    lon_lines=np.linspace(lon_min, lon_max, n_blocks)

    #Plotting
    display.plot_ppi_map( 'ZEROS',
                          lat_0= lat_0,
                          lon_0= lon_0,
                          max_lat=lat_max, min_lat=lat_min,
                          max_lon=lon_max, min_lon=lon_min,
                          lat_lines= lat_lines,
                          lon_lines= lon_lines,
                          resolution= '10m',
                          vmin= vmin, vmax= vmax,
                          projection= projection,
                          fig= fig, ax= ax,
                          title= title,
                          cmap= cm.get_cmap('GnBu'),
                          #olorbar_flag=False
                        )
    display.plot_point(lon_0, lat_0,label_text='Radar')

    #Axis
    ax.xaxis.set_tick_params(rotation=35)
    ax.set_aspect("equal")
    # ax.xaxis.label.set_size(50)

    if( middle_points ):
        mp= get_middle_points( lon_lines, lat_lines )
        
        lon= [ point[0] for point in mp ]
        lat= [ point[1] for point in mp ]

        data= radar.fields[ field ]['data']

        radar_at_gages= get_acum_by_gages( lon, lat, data, nnear)

        gages= [ gage for gage in radar_at_gages ]

        if nnear > 1:
            #gages= [ round(sum(gage)) if round(sum(gage)) < max_val else max_val for gage in gages ]
            gages= [ round(sum(gage)) for gage in gages ]
        else:
            gages= [ round(gage) for gage in gages ]

        plot_labels( display, gages, mp)
        

    #savefig
    plt.savefig( filename )

    #np.rot90(np.reshape(gages, (9,9)),3)
    return gages, mp#, (lon_lines, lat_lines)

def plot_heat_map( gages:list , filename, vmax=3000):
    plt.cla()
    plt.clf()
    
    n= int(np.sqrt( len(gages) ))
    data= np.rot90(np.reshape( gages, (n,n)),3 )

    plt.imshow( data, vmin=0, vmax=vmax, cmap='GnBu', aspect='auto' )

    plt.xticks([])
    plt.yticks([])
    
    plt.colorbar() 
    plt.savefig( filename )

def plot_field_labels_section( radar, field:str, display:pyart.graph.RadarMapDisplay,  fig, projection,title:str, filename:str, lat_max:float= 19.8, lat_min:float= 21.7,lon_max:float= -100.59, lon_min:float= -99.0, n_blocks:int= 15, vmin:int= 0, vmax:int= 200, middle_points:bool=True, max_val:float=8000):

    #Figure
    ax= fig.add_subplot( 1,1,1, projection= projection )

    #Radar coords
    lon_0, lat_0= get_coords( radar )

    #Lines
    lat_lines=np.linspace(lat_min, lat_max, n_blocks)
    lon_lines=np.linspace(lon_min, lon_max, n_blocks)

    #Plotting
    display.plot_ppi_map( field,
                          lat_0= lat_0,
                          lon_0= lon_0,
                          max_lat=lat_max, min_lat=lat_min,
                          max_lon=lon_max, min_lon=lon_min,
                          lat_lines= lat_lines,
                          lon_lines= lon_lines,
                          resolution= '10m',
                          vmin= vmin, vmax= vmax,
                          projection= projection,
                          fig= fig, ax= ax,
                          title= title,
                          cmap= cm.get_cmap('GnBu'),
                          #colorbar_flag=False
                        )
    display.plot_point(lon_0, lat_0,label_text='Radar')

    #Axis
    ax.xaxis.set_tick_params(rotation=35)
    ax.set_aspect("equal")
    # ax.xaxis.label.set_size(50)

    if( middle_points ):
        mp= get_middle_points( lon_lines, lat_lines )
        
        lon= [ point[0] for point in mp ]
        lat= [ point[1] for point in mp ]

        data= radar.fields[ field ]['data']

        radar_at_gages= get_acum_by_gages( lon, lat, data, 5)
        gages= [ gage for gage in radar_at_gages ]
        gages= [ round(sum(gage)) if round(sum(gage)) < max_val else max_val for gage in gages ]
        plot_labels( display, gages, mp)
        

    #savefig
    plt.savefig( filename )

## Others
## ========================================
def get_acum_by_fields( radar, new_field ,lng_name='Acumulado anual 2015', srt_name='ACUM ANUAL',unit='mm' ):
    acum= np.zeros( (360,921) )
    fields= radar.metadata['field_names'].split(', ')

    for field in fields:
        acum+= radar.fields[field]['data'].filled()
    
    radar.add_field( new_field, numpy_to_radar_dict(
        acum,
        lng_name,
        srt_name,
        unit) )

    return radar

def get_acum_by_gages(lon, lat, data, nnear ):
    radar_at_gages,_,_,_,_,_,_= get_acum_from_coord(lon, lat, data, nnear=nnear)

    return clear_inf_nan( radar_at_gages )

def get_acum_from_coord( lon:int, lat:int, data:np.array, epsg:int=4326, nnear= 1):
    fileData='/home/arielcg/QRO_2015/RAW_NA_000_236_20150711000109'
    r, az, sitecoords= get_metadata( 
                                    get_iris(fileData) )

    proj= wl.georef.epsg_to_osr( epsg )
    x,y= get_proj_transform( lat, lon, epsg)

    polarneighbs= wl.verify.PolarNeighbours( r, az, sitecoords, proj, x,y, nnear= nnear)
    
    radar_at_gages= polarneighbs.extract( data )
    binx, biny = polarneighbs.get_bincoords()
    binx_nn, biny_nn= polarneighbs.get_bincoords_at_points()

    return radar_at_gages,x,y,binx,biny,binx_nn,biny_nn

def get_proj_transform( lat:list, lon:list, epsg:int ):
    if( len( lat ) != len( lon ) ):
        raise ValueError(" Las dimensiones de las coordenadas no coinciden")

    crs= CRS.from_epsg( epsg )
    proj= Transformer.from_crs(crs.geodetic_crs,crs)

    t_lat= []
    t_lon= []

    for lo, la in zip( lon, lat ):
        LAT, LON= proj.transform(  la, lo)
        t_lat.append(LAT)
        t_lon.append(LON)

    return np.array( t_lon ), np.array( t_lat )


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
    return list( itertools.product(new_X, new_Y) )

    #Inteta obtener la mitad de la linea y luego la mitad de la linea y luego haces pares para que obtengas los medios 

def get_acum_DataFrame( names:list, coords:list, acums:list )->pd.DataFrame:
    return pd.DataFrame({
        'names': names,
        'lon': coords[0],
        'lat': coords[1],
        'acum': acums
        })

def clear_inf_nan( acums:list, nan_value:float= 0.0, inf_value:float=0.0 )->list:
    """Get a list of acum from a local neighborhood and change nan or inf values whit nan_value and inf_value, respectively

    :param acums: List of acum from neighborhoods
    :type acums: list
    :param nan_value: New values for nan, defaults to 0.0
    :type nan_value: float, optionl
    :param inf_value: New value for inf, defaults to 0.0
    :type inf_value: float, optional
    :return: A list whitout nan an inf values
    :rtype: list
    """
    
    new_acum= []
    for acum in acums:
        if( type(acum) == list or type(acum) == np.ndarray ):
            aux_acum= []
            for value in acum:
                if( ( isinf( value ) ) or ( isnan( value ) ) ):
                    aux_acum.append( isinf(value)*inf_value + isnan(value)*nan_value )
                else:
                    aux_acum.append( value )
            new_acum.append( aux_acum )
            
        else:
            
            if( ( isinf( acum ) ) or ( isnan( acum ) ) ):
                new_acum.append( isinf(acum)*inf_value + isnan(acum)*nan_value )
            else:
                new_acum.append( acum )
    return new_acum
                

def get_m_b( X1:tuple, X2:tuple)->tuple:
    """y= mx + b

    :param X1: _description_
    :type X1: tuple
    :param X2: _description_
    :type X2: tuple
    :return: _description_
    :rtype: tuple
    """
    m= ( X2[1] - X1[1] ) / ( X2[0] - X1[0] )
    b= X1[1] - m*X1[0]

    return m,b

def get_all_fields( radar ):
    return radar.metadata['field_names'].split(', ')

def get_acum_from_fields( radar, fields ):
    acum= np.zeros((360, 921))
    for field in fields:
        try:
            acum+= radar.fields[ field ]['data'].filled()
        except:
            acum+= radar.fields[ field ]['data']
    return acum 

def get_vn_neig( matrix, coords ):
    
    if coords[1] == 0:
        up= 0
    else:
        up= matrix[ coords[0]][ coords[1] - 1 ]
    if  coords[1] == matrix.shape[1] - 1 :
        down= 0
    else:
        down= matrix[ coords[0]][ coords[1] + 1 ]
    if coords[0] == 0:
        right= 0
    else:
        right= matrix[ coords[0] - 1][ coords[1] ]
    if  coords[0] == matrix.shape[0] - 1:
        left= 0
    else:
        left= matrix[ coords[0] + 1][ coords[1] ]
        

    return( [ up, left, down, right  ] )

def PE( val:float )->float:
    """La precipitación efectiva se refiere a la parte de la lluvia que puede ser efectivamente utilizada por plantas de forma empirica vamos a usar la ecuación FAO/AGLW

    :param val: Precipitación en mm
    :type val: float
    :return: Precipitación efectiva en mm
    :rtype: float
    """

    f1= lambda x: 0.6 * x - 10
    f2= lambda x: 0.8 * x - 24

    return f2( val ) if val > 70 else f1( val )

def VAN( n:int, c:float, p:int ):
    """Brito aplica la siguiente relación para estimar el consumo de la familia

    :param n: Número de personas en la vivienda
    :type n: int
    :param c: Consumo medio de agua por presona por dia
    :type c: float
    :param p: PEriodo de consumo considerado
    :type p: int
    """

    return n * c * p

def PA( mm:float,  s:float, c:float= 0.85 )->float:
    """Superficie de techo multiplicada por los milímetros de lluvia que cen en tu región y multiplicado por el coeficiente de captación

    :param mm: Milimetros de lluvia
    :type mm: float
    :param c: Coeficiente de captación
    :type c: float
    :param s: Superficie de techo
    :type s: float
    :return: Volumne de agua cosechable
    :rtype: float
    """

    return mm * s * c
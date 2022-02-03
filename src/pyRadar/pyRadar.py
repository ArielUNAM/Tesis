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

# Acquisition and ordering
# ========================================
def get_dict_of_data_path(path_to_data:str)->dict:
    """Returns a dictionary of dictionaries that stores the location of the data classified by month and day; having this data as the keys.

    :param path_to_data: Path to data radar
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

def get_basenames_of(words:list,word_length:int)->list:
    """Return the basenames of radar data without the date information.

    :param words: Names of all data radar.
    :type words: list
    :param word_length: Number of positions where date appears.
    :type word_length: int
    :return: basenames of radar data without the date information.
    :rtype: list
    """
    basenames=[]
    for word in words:
        if ( word[:word_length] not in basenames ):
            basenames.append(word[:word_length])
    return basenames

def get_path_files(root:str, rex:str)->list:
    """Return a list of paths whit base in root and the regular expresion given

    :param root: Root path
    :type root: str
    :param re: Regular expresion
    :type rex: str
    :return: List of paths
    :rtype: list
    """
    return [root + string for string in os.listdir(root) if re.match(rex,string)]

# Data reading and processing Wradlib
# ========================================
def est_rain_rate_z(path_to_data,pia_type:str='default',tr1:float=12,n_p:float=12,tr2:float=1.1,a:float = 200,b:float = 1.6,intervalos:int = 390,mult=True,bool_vel:bool= True,angle:float=1):
    iris_data= get_iris_data( path_to_data )

    if( get_elevation(iris_data,True) < angle ):
        dBZ, pia= data_processing_chain(iris_data,pia_type,tr1,n_p,tr2,)
        velocity= get_velocity(iris_data,bool_vel)
        return reflectivity_to_rainfall(dBZ+pia,velocity,a,b,intervalos,mult)
    
    return np.array([])

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
    return gate_0 + gate_size * np.arange(nbins, dtype='float32')

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


# Data reading and processing pyart
# ========================================

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
        dic_of_data= get_dict_of_data_path(path2root+path)
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
    acum= np.zeros(shape)
    for file in files[:3]:
        rain= est_rain_rate_z( path2data + file)
        acum+= rain

    return acum

def set_radar(path_to_file,path_to_save,dic,name):
    radar= get_radar(path_to_file)
    
    keys= radar.fields.copy()
    keys= keys.keys()
    for key in keys:
        radar.fields.pop(key)
    
    for key, value in dic.items():
        radar.add_field(key,value,replace_existing=True)
    
    pyart.io.write_cfradial(path_to_save+name+'.nc', radar)

def get_dic_radar_data(data,long_name):
    dic= {'units':'dBZ',
          'standard_name': 'equivalent_reflectivity_factor',
          'long_name':long_name,
          'coordinates': 'elevation azimuth range',
          'data':data}
    return dic

def get_acum_by_dict_radar(dic):
    acum= 0
    for key in dic.keys():
        acum+= dic[key]['data']

    print('acum')
    return acum

def get_acum_by_list(path_to_file:str,files:list,angle:float=1):
    radar= get_radar( path_to_file + files[0] )

    acum= np.zeros( ( radar.nrays, radar.ngates) )
    for _file in files[:10]:

        acum+= est_rain_rate_z( path_to_file + _file )

    return acum, path_to_file + files[0]

# Classes
## Reading
## ========================================
# class createRadarWL(radar_manipulator):
#     def __init__(self,filename:str) -> None:
#         super().__init__()
#         self.iris= get_iris_data(filename)

    
## Plotting
## ========================================
class radar_manipulator(object):
    def __init__(self)->None:
        pass

    def plot_ppi_wrl(self,name,radar_data:np.ndarray,vlim:list,path:str):
        """PPI, Plan Position Indicator, correspondiente con la reflectividad registrada en cada una de las elevaciones y que se proyecta sobre el plano horizontal"""
        fig= plt.figure()
        _,cf= wl.vis.plot_ppi(radar_data,
                                cmap='ocean',fig=fig,   
                                vmin=vlim[0], vmax=vlim[1])
        plt.xlabel("xlabel")
        plt.ylabel("ylabel")
        plt.title("title")
        cf= plt.colorbar(cf, shrink=0.8)
        cf.set_label("mm")
        plt.grid(color="gray")
        plt.savefig(path+name+"ppi_wrl.png")
        
    def plot_ppi_art(self,name,radar_data,vlim,path,source="/home/arielcg/QRO_2015/"):
        fig= plt.figure()
        radar= pyart.io.read_rsl(source+'RAW_NA_000_236_20150711000109')
        level0= radar.extract_sweeps([0])

        level0.add_field('acum',radar_data)
        display= pyart.graph.RadarDisplay(level0)
        ax= fig.add_subplot(111)
        display.plot('acum', 0, title="title", vmin=vlim[0],vmax=vlim[1],  colorbar_label='', ax=ax)
        display.plot_range_ring(radar.range['data'][-1]/1000., ax=ax)
        plt.savefig(path+name+"ppi_art.png")

    def plot_clutter_wrl(self,reflectivity:np.ndarray,wsize=5,
                            thrsnorain=0.,
                            tr1=6.,
                            n_p=8,
                            tr2=1.3):
        clmap= get_clutter(reflectivity,
                                wsize=5,
                                thrsnorain=0.,
                                tr1=6.,
                                n_p=8,
                                tr2=1.3)
        fig = plt.figure(figsize=(12,8))
        ax = fig.add_subplot(121)
        ax, _ = vis.plot_ppi(reflectivity, ax=ax)
        ax.set_title('Reflectivity')
        ax = fig.add_subplot(122)
        ax, _ = vis.plot_ppi(clmap, ax=ax)
        ax.set_title('Cluttermap')
        plt.savefig("../data/img/clutter_map.png")
        
    def plot_geo_ppi_art(self,acum_data:np.ndarray):
        try:
            radar= pyart.io.read_sigmet(acum_data)
        except:
            radar= pyart.io.read(acum_data)
        display = pyart.graph.RadarMapDisplay(radar)

        # Setting projection and ploting the second tilt
        projection = ccrs.LambertConformal(central_latitude=radar.latitude['data'][0],
         central_longitude=radar.longitude['data'][0])

        fig = plt.figure( figsize=(6,6) )
        
        ax= fig.add_subplot(1,1,1,projection=projection)
        
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.OCEAN, facecolor='#CCFEFF')
        ax.add_feature(cfeature.LAKES, facecolor='#CCFEFF')
        ax.add_feature(cfeature.RIVERS, edgecolor='#CCFEFF')
        ax.add_feature(cfeature.LAND, facecolor='#FFE9B5')
        ax.add_feature(cfeature.STATES, edgecolor='black', zorder=10)

        display.plot_ppi_map('reflectivity', vmin=0, vmax=80,
                        resolution='10m', projection=projection,
                        fig=fig, lat_0=radar.latitude['data'][0],
                        lon_0=radar.longitude['data'][0])

        # Indicate the radar location with a point
        display.plot_point(radar.longitude['data'][0], radar.latitude['data'][0])
        plt.savefig("prueba")
    
    def plot_rain_gauge_locations(self,acum_data:np.ndarray,figsize=(12,12))->None:
        """Routine verification measures for radar-based precipitation estimates

        :param acum_data: Archivo a leer
        :type acum_data: np.ndarray
        :param figsize: Tamaño de la figura, defaults to (12,12)
        :type figsize: tuple, optional
        """
        _, x,y,binx,biny,binx_nn,biny_nn= self.bin_precipitation_estimates(acum_data)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(121)
        ax.plot(binx, biny, 'r+')
        ax.plot(binx_nn, biny_nn, 'b+', markersize=10)
        ax.plot(x, y, 'bo')
        ax.axis('tight')
        ax.set_aspect("equal")
        plt.title("Full view")
        ax = fig.add_subplot(122)
        ax.plot(binx, biny, 'r+')
        ax.plot(binx_nn, biny_nn, 'b+', markersize=10)
        ax.plot(x, y, 'bo')
        plt.xlim(binx_nn.min()-5, binx_nn.max()+5)
        plt.ylim(biny_nn.min()-7, biny_nn.max()+8)
        ax.set_aspect("equal")
        txt = plt.title("Zoom into rain gauge locations")
        plt.tight_layout()
        plt.savefig("../data/img/rgl.png")
        
    def bin_precipitation_estimates(self,acum_data,nnear=1,epsg=4326,source='/home/arielcg/QRO_2015/',filename='RAW_NA_000_236_20150711000109'):
        
        iris= get_iris_data(source+filename)
        r= get_range(iris)
        az = np.linspace(0,360,361)[0:-1]
        sitecoords= get_coordinates(iris)

        proj= wl.georef.epsg_to_osr(epsg)
        x,y= get_project_trasnform(FILEBASE, epsg)

        polarneighbs= wl.verify.PolarNeighbours(r,az,sitecoords,proj,x,y,nnear=nnear)

        radar_at_gages= polarneighbs.extract( acum_data['data'] )
        binx, biny = polarneighbs.get_bincoords()
        binx_nn, biny_nn= polarneighbs.get_bincoords_at_points()

        return radar_at_gages, x,y,binx,biny,binx_nn,biny_nn


    def radar_bin_precipitation_estimates(self,data, rnge, azimuth, sitecoords,nnear=1,epsg=4326):
        proj= wl.georef.epsg_to_osr(epsg)
        x,y= get_project_trasnform(FILEBASE, epsg)

        polarneighbs= wl.verify.PolarNeighbours(rnge,azimuth,sitecoords,proj,x,y,nnear=nnear)

        radar_at_gages= polarneighbs.extract( data )
        binx, biny = polarneighbs.get_bincoords()
        binx_nn, biny_nn= polarneighbs.get_bincoords_at_points()

        return radar_at_gages,x,y,binx,biny,binx_nn,biny_nn

        
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


#########################

# radar_manipulator= create_radar_manipulator()
# #radar_manipulator.plot_ppi_art("prueba",np.load(p),[0,100],'.')
# #radar_manipulator.plot_rain_gauge_locations(np.load(p))
# radar_at_gages, x,y,_,_,_,_= radar_manipulator.bin_precipitation_estimates(np.load(p))
# #print(radar_at_gages, x,y,binx,biny,binx_nn,biny_nn)
# df= pd.DataFrame([radar_at_gages, x,y]).transpose()
# df.to_csv("../data/precipitation/prueba.csv",index=False,header=['rain','lon','lat'])

# path_to_data= "/home/arielcg/QRO_2016/"
# path2save= "/home/arielcg/Documentos/Tesis/src/data/radar/"
# radar_acum_year(path_to_data,path2save,'2016')

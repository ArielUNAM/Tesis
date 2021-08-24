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
import wradlib.georef as georef
import wradlib as wl
import pyart


# Data processing libraries
# ================
import numpy as np
import numpy.ma as ma
from collections import OrderedDict
import datetime
import pandas as pd

# Graphical libraries
# ==================
import matplotlib.pyplot as plt
from tqdm import tqdm
from pyproj import CRS
from pyproj import Transformer  

# System libraries
# =================
import os

# VARIABLES
# =================
MONTHS_LIST= ['01','02','03','04','05','06','07','08','09','10','11','12']
SCANN_RANGE= [236000,921]
PARAM_VEL= [0,1]
PARAM_TRANS=[74,1.6,True]
ELEVATION= 1
FILEBASE= 'src/data/base/sacest2.csv'

# Acquisition and ordering of information
# ========================================
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

def get_dict_of_data_path(path_to_data:str)->dict:
    """Returns a dictionary of dictionaries that stores the location of the data classified by year, month and day; having this data as the keys.

    :param path_to_data: Path to data radar
    :type path_to_data: str
    :return: A dictionary of dictionaries of data radar
    :rtype: dict
    """
    orderList= sorted(os.listdir(path_to_data))
    n= get_word_length_until(orderList[0],'_')
    orderDicMon= get_dict_of_data_by_month(orderList,n)

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

def get_word_length_until(word:str,symbol:str)->int:
    """Return the length of a word until a defined symbol appears

    :param word: Word to measure
    :type word: str
    :param symbol: Symbol to stop the measure
    :type symbol: str
    :return: The length of a word until a defined symbol appears
    :rtype: int
    """
    n= len(word) - 1
    while (True):
        if ( word[n] == symbol ):
            break
        else:
            n-= 1
    return n+1

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

# Data reading and processing
# ========================================
def reflectivity_to_rainfall(dBZ:np.ndarray,vel:np.ndarray,a:float = 200,b:float = 1.6,intervalos:int = 390,mult=True)->np.ndarray:
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
        return np.multiply(vel,depth)
    else:
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
        pia= pia_processing(
            dBZ_ord,
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

def clutter_processing(reflectivity:np.ndarray,tr1:float=12,n_p:float=12,tr2:float=1.1)->np.ndarray:
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
    desorden = wl.clutter.filter_gabella(reflectivity,
                                         tr1=tr1,n_p=n_p, tr2=tr2)
    return wl.ipol.interpolate_polar(reflectivity,desorden)

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

def get_range(iris_data:OrderedDict):
    nbins=(iris_data['product_hdr']['product_end']['number_bins'])
    gate_0 =(iris_data['ingest_header']['task_configuration']['task_range_info']['range_first_bin']/100)
    gate_nbin =(iris_data['ingest_header']['task_configuration']['task_range_info']['range_last_bin']/100)
    gate_size=round((gate_nbin - gate_0)/(nbins))
    return gate_0 + gate_size * np.arange(nbins, dtype='float32')

def get_version(iris_data:OrderedDict)->str:
    return iris_data['product_hdr']['product_end']['iris_version_created']

def get_elevation(iris_data:OrderedDict)->np.ndarray:
    return iris_data['data'][1]['sweep_data']['DB_DBT']['ele_start']

def get_velocity(iris_data:OrderedDict, maskedVal:float=None, unmmaskedVal:float=None, processing:bool=False)->np.ndarray:
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
    vel= iris_data['data'][1]['sweep_data']['DB_VEL']['data']

    if ( processing ):
        if ( unmmaskedVal != None ):
            vel[~vel.mask] = unmmaskedVal

        if ( maskedVal == None ):
            vel.mask= ma.nomask
        else:
            vel.mask= maskedVal
    
        return vel
    else:
        return vel

def get_reflectivity(iris_data:OrderedDict)->np.ndarray:
    """Return the reflectivity of a iris data.

    Precipitation intensity is measured by a ground-based radar that bounces radar waves off of precipitation. The Local Radar base reflectivity product is a display of echo intensity (reflectivity) measured in dBZ (decibels).


    :param iris_data: [description]
    :type iris_data: OrderedDict
    """
    return iris_data['data'][1]['sweep_data']['DB_DBZ']['data']

def get_coordinates(iris_data:OrderedDict)->tuple:
    """Return the lat and lon of a iris data

    :param iris_data: [description]
    :type iris_data: OrderedDict
    :return: [description]
    :rtype: tuple
    """
    return(iris_data['product_hdr']['product_end']['latitude'],
          iris_data['product_hdr']['product_end']['longitude'])

def get_iris_data(path_iris:str)->dict:
    """Return an wradlib file type of iris file

    :param path_iris: Path to iris file
    :type path_iris: str
    :return: Dictionary with data and metadata retrieved from file.
    :rtype: OrderedDict
    """
    return wl.io.iris.read_iris(path_iris)

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

# Plotting
# ========================================
class create_radar_manipulator(object):
    def __init__(self)->None:
        pass

    def plot_ppi_wrl(self,name,radar_data:np.ndarray,vlim:list,path:str):
        """PPI, Plan Position Indicator, correspondiente con la reflectividad registrada en cada una de las elevaciones y que se proyecta sobre el plano horizontal"""
        fig= plt.figure()
        _,cf= wl.vis.plot_ppi(radar_data,
                                cmap='viris',fig=fig,   
                                vmin=vlim[0], vmax=vlim[1])
        plt.xlabel("xlabel")
        plt.ylabel("ylabel")
        plt.title("title")
        cf= plt.colorbar(cf, shrink=0.8)
        cf.set_label("mm")
        plt.grid(color="gray")
        plt.savefig(path+name+"ppi_wrl.png")
        
    def plot_ppi_art(self,name,radar_data,vlim,path):
        fig= plt.figure()
        radar= pyart.io.read_rsl('/home/arielcg/QRO_2015/'+'RAW_NA_000_236_20150711000109')
        level0= radar.extract_sweeps([0])

        level0.add_field('acum',radar_data)
        display= pyart.graph.RadarDisplay(level0)
        ax= fig.add_subplot(111)
        display.plot('acum', 0, title="title", vmin=vlim[0],vmax=vlim[1],  colorbar_label='', ax=ax)
        display.plot_range_ring(radar.range['data'][-1]/1000., ax=ax)
        plt.savefig(path+name+"ppi_art.png")

    def plot_capi(self):
        """CAPPI, Constant Altitude Plan Position Indicator, este segundo tipo de imagen trata de representar la reflectividad registrada sobre un plano a una altura constante. Para generar este segundo tipo de imagen se utilizan aquellos fragmentos de información de las diversas elevaciones que se encuentran más cerca de la altura para la que se quiere generar el CAPPI"""
        pass

    def plot_rhi(self):
        """mantener la antena fija en una dirección (o azimut respecto al noreste) y realizar una lectura incrementando el ángulo de elevación de la antena. Es lo que se conoce como muestreo en Range Height Indicator (RHI)."""

    def acum_over_a_point(self,acum_data:np.ndarray, latitud:str,longitud:str,filebase:str=FILEBASE,code:int=4485,nnear:int=1):
        """get acumulated precipitation over a specific coords"""
        crs= CRS.from_epsg(code)
        df= pd.read_csv(filebase,delimiter=',')
        X, Y= get_project_trasnform(df,Transformer.from_crs(crs.geodetic_crs,crs))
        az= np.linspace(0,360,361)[0:-1]
        proj= georef.epsg_to_osr(code)

        site_coords= get_coordinates(iris_data)
        range_rad= get_range(iris_data)

        polar_neighbours= wl.verify.PolarNeighbours(range_rad, az, site_coords, proj, X, Y, nnear=nnear)

        radatr_at_gages= polar_neighbours.extract(acum_data)

        return radatr_at_gages

def get_project_trasnform(df,proj):
    x=y=[]
    for i in range(df.shape[0]):
        X,Y= proj.transform(df.latitud[i],df.longitud[i])
        x.append(X)
        y.append(Y)

    return np.array(x), np.array(y)
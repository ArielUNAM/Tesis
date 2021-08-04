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

# Radar modules
# ================
from numpy.core.fromnumeric import shape
import wradlib as wl
import pyart

# Data processing
# ================
import numpy as np
import numpy.ma as ma
from collections import OrderedDict
import datetime
import re
from calendar import monthrange

# Graphical modules
# ==================
import matplotlib.pyplot as plt

# System modules
# =================
import os

from tqdm import tqdm
# VARIABLES
# =================
MONTHS_LIST= ['01','02','03','04','05','06','07','08','09','10','11','12']
SCANN_RANGE= [236000,921]
PARAM_VEL= [0,1]
PARAM_TRANS=[74,1.6,True]
ELEVATION= 1

# Processing functions
#######################
def radarDataProcessingChain(data:OrderedDict, pia:int=1,elev:list= [], dist:int= -1, shape: int= -1):
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
        dBZ= np.nan_to_num(dBZ, copy=False, nan=0, posinf=0, neginf=0)
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
    if (pia == 1):
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
    else:
        pia_kraemer = wl.atten.correct_attenuation_constrained(
        dBZ_ord,
        a_max=1.67e-4,
        a_min=2.33e-5, n_a=100,
        b_max=0.7, b_min=0.65,
        n_b=6, gate_length=1.,
        constraints=
        [wl.atten.constraint_dbz,
        wl.atten.constraint_pia],
        constraint_args=
        [[59.0],[20.0]])

    pia_kraemer= np.nan_to_num(pia_kraemer, copy=False, nan=0, posinf=0, neginf=0)
    return dBZ_ord, pia_kraemer

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
    dBZ= np.nan_to_num(dBZ, copy=False, nan=0, posinf=0, neginf=0)

    Z = wl.trafo.idecibel(dBZ)
    R = wl.zr.z_to_r(Z,a=a,b=b)
    V = wl.trafo.r_to_depth(R,intervalos)

    V= np.nan_to_num(V, copy=False, nan=0, posinf=0, neginf=0)
    #print('Multiply')
    #print("Vel: ",vel.data.max())

    #print("Z: ",np.max(Z.data))
    #print("R: ",np.max(R.data))
    #print("V: ",np.max(V.data))

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
        
def ppi(fig,acum,title="Title",xlabel="xlabel",ylabel="ylabel",cmap="viridis",vmin:float=0,vmax:float=120):
    
    ax, cf = wl.vis.plot_ppi(acum, cmap=cmap,fig=fig,vmin=vmin,vmax=vmax)
    #ax, cf = wl.vis.plot_ppi(acum,fig=fig)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    cf = plt.colorbar(cf, shrink=0.8)
    cf.set_label("mm")
    #plt.xlim(-128,128)
    #plt.ylim(-128,128)
    plt.grid(color="grey")
    plt.savefig(title+".png")
    
def ppi2(path1:str,filename:str,path2,filebase:str,title:str,save:bool=True):

    radar = pyart.io.read_rsl(path2+filebase)
    level0=radar.extract_sweeps([0])
    acumula= np.load(path1+filename)
    level0.add_field('acum', acumula)
    display = pyart.graph.RadarDisplay(level0)
    fig = plt.figure(figsize=(20, 20))
    ax = fig.add_subplot(111)
    display.plot('acum', 0, title=title,  vmin=0, vmax=150, colorbar_label='', ax=ax)
    display.plot_range_ring(radar.range['data'][-1]/1000., ax=ax)
    display.set_limits(xlim=(-240, 240), ylim=(-240, 240), ax=ax)#Esto es los rangos del radar
    if ( save ):
        plt.savefig(filename+".png")

# Get info functions
####################
def getVel(data:OrderedDict, maskedVal:float=None, unmmaskedVal:float=None, processing:bool=False):
    """Devuelve un maskedArray de los valores de velocidad

    Dado un objeto radar, se extrae los datos de velocidad que de origen son del tipo masked array. Si lo solicita el usuario, se hace un procesamieno de la información modificando los valores del array.

    Parameters
    ----------
    data : OrderedDict
        Objeto radar
    maskedVal : float, optional
        Valor que se le asignara a los valores enmascarados, by default None
    unmmaskedVal : float, optional
        Valor que se le asignara a los valores no enmascarados. Sino se le da valor se conservan los originales, by default None
    processing : bool, optional
        Define si quiere, o no, cambiar los datos, by default True

    Returns
    -------
    numpy masked array
        masked array de la velocidad
    """
    vel= data['data'][1]['sweep_data']['DB_VEL']['data']

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

def getCoord(fcontent):
    return(fcontent['product_hdr']['product_end']['latitude'],
          fcontent['product_hdr']['product_end']['longitude'])

def getElev(fcontent,elev)->bool:
    #print(fcontent['product_hdr']['product_configuration']['product_name'])
    #print(fcontent['data'][1]['sweep_data']['DB_DBT']['ele_start'].mean())
    #print(fcontent['data'][1]['sweep_data']['DB_DBT']['ele_stop'].mean())
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
    #print(range_rad[-1],range_rad.shape[0])
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
def getWeekNumber(year:int,month:int,day:int)-> int:
    ''' Devuelve el número de la semana de una fecha en particular
    '''
    return datetime.date(int(year), int(month), int(day)).isocalendar()[1]

def getAcumBy(By,Fpath,Dpath)->object:
    '''Devuelve el acumulado segun el tipo indicado
    '''
    pass

def get_names(path:str,n:int=15) -> dict:      
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

### Funciones de Ejecucion
# ===================
def radar2numpy(filename,fpath,elevation,l_range,l_vel,l_params):
    rd= read(filename,fpath)
    V= 0
    if ( getRange(rd,l_range[0],l_range[1]) and getElev(rd,elevation) ):
        vel= getVel(rd,l_vel[0],l_vel[1])
        dBZ_ord, pia= radarDataProcessingChain(rd)
        V= dBZ_to_V(dBZ_ord+pia,vel,l_params[0],l_params[1],l_params[2])

    return V

def get_unique(names,n:int=15)->list:
    basename= []
    for name in names:
        if ( name[:n] not in basename ):
            basename.append(name[:n])
            
    return basename

def getDataByDay(year,month,day,fpath,elevation,l_range,l_vel,l_params):
    basename= get_unique(os.listdir(fpath))           
    for i in range(len(basename)):
        name= basename[i]+year+month+day
        names= os.listdir(fpath)
        
        names= list(filter(lambda x: x if name==x[:len(name)] else 0,names))
        names= list(set(names))

        try:
            names.pop(names.index(0))
        except:
            pass

        if ( names ):
            break
        
    names= list(set(names))
    acum= 0
    for name in names:
        acum= radar2numpy(name,fpath,elevation,l_range,l_vel,l_params)
    
    return acum
        
def get_strlistofnubers(n:int):
    l= []
    for i in range(1,n+1):
        if ( i < 10 ):
            l.append('0'+str(i))
        else:
            l.append(str(i))
    return l

def mkdir(name,path):
    list_dir= os.listdir(path)
    if ( name not in list_dir ):
        name= path+name
        os.mkdir(name)

def saveday(root,files,save,year):
    acum_daily=0
    path= root+files
    names= sorted(os.listdir(path))         
    basenames= get_unique(names)

    mkdir(year,save)

    if ( len(basenames) > 1 ):
        print('basenames:',basenames)
    else:
        for month in MONTHS_LIST:
            DAYS_LIST= get_strlistofnubers(monthrange(int(year), int(month))[1])
            for day in tqdm(DAYS_LIST):
                acum_daily= getDataByDay(year,month,day,path,ELEVATION,SCANN_RANGE,PARAM_VEL,PARAM_TRANS)

                if ( type(acum_daily) != int ):
                    mkdir(month,save+year+'/')
                    n_week= getWeekNumber(year,month,day)
                    n_week= '0' + str(n_week) if n_week < 10 else str(n_week)
                    mkdir(n_week,save+year+'/'+month+'/')

                    try:
                        spath= save+year+'/'+month+'/'+n_week
                        np.savez_compressed(spath+"/radar_{}_{}_{}.npz".format(year,month,day),data=acum_daily.data)

                    except Exception as e:
                        print(e)
                        print("Error to export data_{}_{}_{}".format(year,month,day))
def find(name, path):
    for _, _, files in os.walk(path):
        if name in files:
            #return os.path.join(root, name)
            return True
        else:
            return False

def saveweek(root):
    years= os.listdir(root)
    years= [year for year in years if os.path.isdir(root+year)]
    for year in years:
        meses= os.listdir(root+year)
        meses= [mes for mes in meses if os.path.isdir(root+year+'/'+mes)]
        for mes in meses:
            semanas= os.listdir(root+year+'/'+mes)
            semanas= [semana for semana in semanas if os.path.isdir(root+year+'/'+mes+'/'+semana)]
            for semana in semanas:
                dias= os.listdir(root+year+'/'+mes+'/'+semana)
                acum= 0
                for dia in dias:
                    data= np.load(root+year+'/'+mes+'/'+semana+'/'+dia)
                    acum+= data['data']
                try:
                    
                    spath= root+year+'/'+mes
                    np.savez_compressed(spath+"/radar_{}_{}_{}.npz".format(year,mes,semana),data=acum)
                except Exception as e:
                    print(e)
                    print("Error to export data_{}_{}_{}".format(year,mes,semana))

def savemonth(root):
    years= os.listdir(root)
    years= [year for year in years if os.path.isdir(root+year)]
    for year in years:
        meses= os.listdir(root+year)
        meses= [mes for mes in meses if os.path.isdir(root+year+'/'+mes)]
        for mes in meses:
            semanas= os.listdir(root+year+'/'+mes)
            semanas= [semana for semana in semanas if not os.path.isdir(root+year+'/'+mes+'/'+semana)]
            acum= 0
            for semana in semanas:
                data= np.load(root+year+'/'+mes+'/'+semana)
                acum+= data['data']
            try:
                spath= root+year
                np.savez_compressed(spath+"/radar_{}_{}.npz".format(year,mes),data=acum)
            except Exception as e:
                print(e)
                print("Error to export data_{}_{}".format(year,mes))


def saveyear(root):
    years= os.listdir(root)
    years= [year for year in years if os.path.isdir(root+year)]
    for year in years:
        meses= os.listdir(root+year)
        meses= [mes for mes in meses if not os.path.isdir(root+year+'/'+mes)]
        acum= 0
        for mes in meses:
            data= np.load(root+year+'/'+mes)
            acum+= data['data']
        try:
            spath= root
            np.savez_compressed(spath+"/radar_{}.npz".format(year),data=acum)
        except Exception as e:
            print(e)
            print("Error to export data_{}".format(year))
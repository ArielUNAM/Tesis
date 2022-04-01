import site
import sys
from turtle import color
sys.path.append('../')

from src.pyRadar.dataPaths import *
import src.pyRadar.pyRadar as pr

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pyart
import cartopy.crs as ccrs 

def plot_moth_acum():
   paths= pr.get_path_files( path2save, "201[0-9]" ) 

   for path in paths:
       files= pr.get_path_files( path + '/', 'qro_radar_acum')
       radar= pr.get_radar( files[0] )
       vmax= [100 for _ in range( len(radar.fields.keys()))]
       plot_radar_gen( radar, path2fig + "month"+path[-4:]+"PR", vmax=vmax)

def generate_radar_acum_trim(trim=3):
    paths= pr.get_path_files( path2save, "201[0-9]" ) 
    
    for path in paths:
        files= pr.get_path_files( path+'/', 'qro_radar_acum')

        radar= pr.get_radar( files[0] )
        radar_subplots= list( radar.fields.keys() )

        base_radar= pr.clear_radar( pr.get_radar( radar_name_base ) )

        n= len(radar_subplots)
        m_acum= np.zeros((360,921), dtype=np.float64)
        for i in range( n ):
            m_acum+= radar.fields[ radar_subplots[i] ][ 'data' ].filled()
            if( (i+1) % trim == 0 ):
                radar_dic= pr.numpy_to_dict( m_acum, f"Acumulado trimestral para {path[-4:]}",f'ACUM_TRI_{ (i+1)/3 }',"Precipitación acumulada [$mm h^-1$]")
                base_radar.add_field( f'ACUM_TRI_{ (i+1)/3 }', radar_dic )

                m_acum= np.zeros((360,921), dtype=np.float64)

        plot_radar_gen( base_radar, path2fig + "monthAcum"+path[-4:]+"PR", vmax=[100, 10, 100, 100])

def generate_radar_acum_year():
    
    paths= pr.get_path_files( path2save, "201[0-9]" )    
    
    base_radar= pr.clear_radar( pr.get_radar( radar_name_base ) )
    
    for path in paths:
        files= pr.get_path_files( path+'/', 'qro_radar_acum')
        radar= pr.get_radar( files[0] )

        radar= pr.get_radar( files[0] )
        radar_subplots= list( radar.fields.keys() )

        y_acum= np.zeros((360,921), dtype=np.float64)
        for month in radar_subplots:
            y_acum+= radar.fields[month]['data'].filled()

        radar_dic= pr.numpy_to_dict( y_acum.astype(np.float64), f"Acumulado anual para {path[-4:]}",f'ACUM_QRO_{path[-4:]}',"Precipitación acumulada [$mm h^-1$]")

        base_radar.add_field( f'ACUM_QRO_{path[-4:]}', radar_dic )

    plot_radar_gen( base_radar, path2fig + "yearAcumPR" )

def plot_radar_gen(radar, filename, vmax= [1000,10,1000],n_cols=3):
    from math import ceil
    radar_subplots= list( radar.fields.keys() )
    n= len( radar_subplots )

    fig= plt.figure(figsize=(25,25))
    n_rows= int(ceil( n / n_cols ))

    projection = ccrs.LambertConformal(central_latitude=radar.latitude['data'][0], central_longitude=radar.longitude['data'][0])

    display= pyart.graph.RadarMapDisplay( radar )

    for i in range( n ):
        try:
            ax = fig.add_subplot(n_rows, n_cols, i+1, projection=projection)
            lat_0= radar.latitude['data'][0]
            lon_0= radar.longitude['data'][0]

            display.plot_ppi_map(radar_subplots[i],0,
                        #width=100, height=100,
                        lat_0=lat_0,
                        lon_0=lon_0,
                        resolution='10m',
                        vmin=0, vmax=vmax[i],
                        projection=projection,
                        fig=fig, ax=ax,
                        #title=f"{radar_subplots[i]}",
                        cmap=cm.get_cmap('GnBu'))
        
        except Exception as e:
            print(radar_subplots[i])
            print(f"Revisa {e}")
            continue
    plt.savefig(filename)

def plot_acums():
    paths= pr.get_path_files( path2save, "201[0-9]?" )    

    for path in paths:
        files= pr.get_path_files( path+'/', 'qro_radar_acum')

        radar= pr.get_radar(files[0])
        radar_subplots= list( radar.fields.keys() )

        display = pyart.graph.RadarMapDisplay( radar )
        fig = plt.figure(figsize=(25,25))

        projection = ccrs.LambertConformal(central_latitude=radar.latitude['data'][0], central_longitude=radar.longitude['data'][0])

        n= 3
        plot(radar,display,fig,n,radar_subplots,projection)
        pr.plt.savefig(path)

def radar_data_exploration():
    """Esta función intenta mostrar cómo usar las funciones
    que se desarrollaron para la tesis y que permite facilitar las 
    operaciones con las bibliotecas de wradlib y pyart. En partícular 
    vamos a graficar la información del radar en todas las partes
    de la cadena de procesamiento.
    """
    #Obtenemos las rutas de los archivos de radar 
    paths= pr.get_path_files( path2root, "QRO_201[0-9]?" )
    
    #Obtenemos los archivos que se encuentran en las rutas
    files= pr.get_files_from_path( paths[0] )

    #Obtenemos el archivo de nuestro interes, para nosotros es julio 15 de 2015
    path_radar_07_15= files['07']['24'][10]

    #Obtenemos el archivo iris
    iris_07_15= pr.get_iris_data( path_radar_07_15 )

    #Obtenemos la metadata
    r, az, coord= pr.get_metadata( iris_07_15 )
    data= pr.get_reflectivity( iris_07_15 )

def plot_section(data, section):
    plt.figure(figsize=(10,8))
    ax, cf = pr.wl.vis.plot_ppi(data, cmap="GnBu")
    plt.xlabel("Rango [km]")
    plt.ylabel("Ragno [km]")
    plt.title('Rayo en un día con lluvia. Julio 17, 2015', y=1.05)
    cb = plt.colorbar(cf, shrink=0.8)
    cb.set_label("Precipitacion")
    #plt.plot([0,-860],[0,-280],"-", color="black", lw=2)

    plt.grid(color="grey")

    plt.savefig('./section')

def pruebas_multiplot():
    radar_name= "/home/arielcg/Documentos/Tesis/src/data/radar/2017/qro_radar_acum.cn"
    radar= pr.get_radar(radar_name)
    radar_subplots= list( radar.fields.keys() )

    display = pyart.graph.RadarMapDisplay( radar )
    fig = plt.figure(figsize=(25,25))

    projection = ccrs.LambertConformal(central_latitude=radar.latitude['data'][0],
         central_longitude=radar.longitude['data'][0])

    n= 3
    plot(radar,display,fig,n,radar_subplots,projection)



def plot(radar,display,fig,n,radar_subplots,projection,xpoint,ypoint):
    m= len(radar_subplots)/n
    lat_max= 19.8; lat_min= 21.7
    lon_max= -100.59; lon_min= -99.0
    for i in range( int(n*m) ):
        try:
            ax = fig.add_subplot(n,m, i+1, projection=projection)
            lat_0= radar.latitude['data'][0]
            lon_0= radar.longitude['data'][0]
    
            lat, lon, _ = radar.get_gate_lat_lon_alt(0)
            lat_lines=np.linspace(lat_min, lat_max, 15)
            lon_lines=np.linspace(lon_min, lon_max, 15)
       

            display.plot_ppi_map(radar_subplots[i],
                        #max_lat=np.amax(lat), min_lat=lat.min(),
                        #min_lon=np.amin(lon), max_lon=lon.max(),
                        #width=100, height=100,
                        max_lat=lat_max, min_lat=lat_min,
                        max_lon=lon_max, min_lon=lon_min,
                        lat_lines= lat_lines,
                        lon_lines= lon_lines,
                        lat_0=lat_0,
                        lon_0=lon_0,
                        resolution='10m',
                        vmin=0, vmax=200,
                        projection=projection,
                        fig=fig, ax=ax,
                        title=f"Acumulado del mes {radar_subplots[i]}",
                        cmap=cm.get_cmap('GnBu'))
            display.plot_point(lon_0, lat_0,label_text='Radar')
            

            ax.xaxis.set_tick_params(rotation=35)
            middle_points= pr.get_middle_points( lon_lines,lat_lines )
            i= 0
            for point in middle_points:
                display.plot_point(point[0], point[1] , 'o',label_text='', color='r')
                i+= 1
            display.plot_line_geo(xpoint,ypoint)
            ax.plot(xpoint, ypoint, 'b+',color='y')
            
            ax.set_aspect("equal")

        except Exception as e:
            print(radar_subplots[i], i)
            print(f"Revisa {e}")
            continue

    
    plt.savefig(f"prueba{i}")
    
    

def plot_cities_2(ax,lats,lons):
    # plot city dots with annotation, finalize plot
    # lat/lon coordinates of five cities in Bangladesh
    i= 0
    for lon, lat, city in zip(lons, lats, str(i)):
        print(lon, lat, city)
        ax.plot(lon, lat, 'ro', zorder=5)
        ax.text(lon + 0.01, lat + 0.01, city, fontsize='large')
        i+= 1

def get_acum_from_coord( lon:int, lat:int, data:np.array, epsg=4326, nnear= 1):
    fileData='/home/arielcg/QRO_2015/RAW_NA_000_236_20150711000109'
    r, az, sitecoords= pr.get_metadata( 
                                    pr.get_iris_data(fileData) )

    proj= pr.wl.georef.epsg_to_osr( epsg )
    x,y= get_proj_transform( lat, lon, epsg)

    polarneighbs= pr.wl.verify.PolarNeighbours( r, az, sitecoords, proj, x,y, nnear= nnear)
    
    radar_at_gages= polarneighbs.extract( data )
    binx, biny = polarneighbs.get_bincoords()
    binx_nn, biny_nn= polarneighbs.get_bincoords_at_points()

    return radar_at_gages,x,y,binx,biny,binx_nn,biny_nn

def get_proj_transform( lat, lon, epsg ):
    if( len( lat ) != len( lon ) ):
        raise ValueError(" Las dimensiones de las coordenadas no coinciden")

    crs= pr.CRS.from_epsg( epsg )
    proj= pr.Transformer.from_crs(crs.geodetic_crs,crs)

    t_lat= []
    t_lon= []

    for lo, la in zip( lon, lat ):
        LAT, LON= proj.transform(  la, lo)
        t_lat.append(LAT)
        t_lon.append(LON)

    return pr.np.array( t_lon ), pr.np.array( t_lat )

def acum_year():
    #Obtención de los archivos del 2017
    path= pr.get_list_of_path_files( path2root, "QRO_2017")
    files= pr.get_dict_of_data_path( path[0] ) 

    t_acum= {}
    for month in files.keys():
        print(f"Start month {month}")
        m_acum= None
        for day in files[ month ].keys():
            for f in files[ month ][ day ][:2]:
                
                s, acum= pr.est_rain_rate_z( f )

                if( m_acum is None ):
                    m_acum= np.zeros( s )
                
                m_acum+= acum
        if(  files[ month ]  ):
            m_radar= pr.get_dic_radar_data( m_acum, f"MONTH_ACUM_{month}" )
            t_acum[month]= m_radar

    radar_base= "/home/arielcg/QRO_2017/RAW_NA_000_236_20170425233109"
    pr.set_radar(radar_base,'.',t_acum,"QRO_ACUM_2017")

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
                        lon_0=radar.longitude['data'][0],ax=ax)

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
        
    def bin_precipitation_estimates(self,acum_data,nnear=1,epsg=4326,fileradar='/home/arielcg/QRO_2015RAW_NA_000_236_20150711000109'):
        
        #Get data info from radar
        iris= get_iris_data(fileradar)
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
 
def plot_reflectivity():
    """Graficas de reflectividad
    """
    iris= pr.get_iris_data( radar_name_base )
    reflectivity= pr.get_reflectivity( iris )
    pr.plot_reflectivity( reflectivity, "Reflectividad", "equivalent reflectivity (dBZ)", path2fig + "refWL" )

    radar= pr.get_radar( radar_name_base )
    pr.plot_reflectivity( radar, "Reflectividad", "equivalent reflectivity (dBZ)", path2fig + "refPR",radarFrom=True )
    
def plot_clutter():
    """Graficas de la aplicación del filtro gabella
    """
    iris= pr.get_iris_data( radar_name_base )
    reflectivity= pr.get_reflectivity( iris )
    pr.plot_clutter( reflectivity, "Filtro Gabella para disminuir el ruido", path2fig+"gabellaWL")
 
def plot_pia():

    iris= pr.get_iris_data( radar_name_base )
    reflectivity= pr.get_reflectivity( iris )

    beam= ([0,-860],[0,-280]) #Get this values manually
    mybeams= slice(250, 255) #This is an angle, get manually

    #First plot
    pr.plot_beam( reflectivity, beam, "Sección del radar analizada", "equivalent reflectivity (dBZ)", path2fig+"beamWL" )

    #Pia plots
    pr.plot_attenuation( reflectivity, mybeams, path2fig+"kreamerWL", ylim=1)

    pr.plot_attenuation( reflectivity, mybeams, path2fig+"harrisonWL",pia_title="PIA according to Hitchfeld and Bordan",beams_title="PIA according to Hitchfeld and Bordan", type="hitchfeld", ylim=1)

    pr.plot_attenuation( reflectivity, mybeams, path2fig+"mkreamerWL",pia_title="PIA according to Kraemer modificado",beams_title="PIA according to Kraemer modificado", type="mkraemer",ylim=1 )

    pr.plot_attenuation( reflectivity, mybeams, path2fig+"harrisonWL",pia_title="PIA according to Harrison",beams_title="PIA according to Harrison", type="harrison", ylim=7)

def plot_acum():
    shape, rainfall= pr.est_rain_rate_z( radar_name_base  )
    pr.plot_reflectivity( rainfall, "LLuvia", "[mm h$^-1$]", path2fig + "rainfallWL" )

def measuere_bins():
    """_summary_
    """
    lon= [ -99.,-99.11357143 ]
    lat= [ 21.78, 21.699428571 ]
    # lon= [ -99.,-99.11357143, -99.22714286, -99.34071429, -99.45428571, -99.56785714, -99.68142857, -99.795, -99.90857143, -100.02214286, -100.13571429, -100.24928571, -100.36285714, -100.47642857, -100.59 ]
    # lat= [ 21.7, 21.56428571, 21.42857143, 21.29285714, 21.15714286, 21.02142857, 20.88571429, 20.75, 20.61428571, 20.47857143, 20.34285714, 20.20714286, 20.07142857,19.93571429, 19.8 ]
    
    #Get data
    filename= "/home/arielcg/Documentos/Tesis/src/data/radar/2016/qro_radar_acum.cn"
    radar= pr.get_radar( filename )
    radar_subplots= list( radar.fields.keys() )
    data= radar.fields[ radar_subplots[0] ][ 'data' ].filled()

    radar_at_gages,x,y,binx,biny,binx_nn,biny_nn= get_acum_from_coord(lon,lat, data, nnear=50)

    #plot_bins(binx,biny,binx_nn,biny_nn,x,y)
    display= pyart.graph.RadarMapDisplay( radar )
    fig= plt.figure( figsize=(25,25))
    n=3
    projection = ccrs.LambertConformal(central_latitude=radar.latitude['data'][0], central_longitude=radar.longitude['data'][0])

    plot(radar,display,fig,n,radar_subplots,projection,binx_nn,biny_nn)

    #Aca tengo una tupla de coordenadas y de valores para cada punto en la cercania del punto graficado
    for coor, gaug in zip( zip(lon,lat),radar_at_gages ):
        print(coor, gaug)


def plot_bins(binx,biny,binx_nn,biny_nn,x,y):
    """Plot the entire radar domain and zoom into the surrounding of the rain gauge locations
    """
    lat_max= 19.8; lat_min= 21.7
    lon_max= -100.59; lon_min= -99.0
    lat_lines=np.linspace(lat_min, lat_max, 15)
    lon_lines=np.linspace(lon_min, lon_max, 15)
    
    fig= plt.figure(figsize=(12,12))
    ax= fig.add_subplot(131)
    ax.plot(binx, biny, 'r+')
    ax.plot(binx_nn, biny_nn, 'b+', markersize=10)
    ax.plot(x, y, 'bo')
    ax.axis('tight')
    ax.set_aspect("equal")
    plt.title("Full view")
    ax = fig.add_subplot(132)
    ax.plot(binx, biny, 'r+')
    ax.plot(binx_nn, biny_nn, 'b+', markersize=10)
    ax.plot(x, y, 'bo')
    plt.xlim(binx_nn.min()-0.09, binx_nn.max()+0.09)
    plt.ylim(biny_nn.min()-0.1, biny_nn.max()+0.15)
    ax.set_aspect("equal")
    txt = plt.title("Zoom into rain gauge locations")
    plt.tight_layout()
    ax = fig.add_subplot(133)
    ax.plot(lat_lines,lon_lines,'o')
    plt.savefig("binsprueba")
    
def density_points():
    lon= [ -99.,-99.11357143 ]
    lat= [ 21.78, 21.699428571 ]

    filename= "/home/arielcg/Documentos/Tesis/src/data/radar/2016/qro_radar_acum.cn"
    radar= pr.get_radar( filename )
    radar_subplots= list( radar.fields.keys() )
    data= radar.fields[ radar_subplots[0] ][ 'data' ].filled()

    radar_at_gages,x,y,binx,biny,binx_nn,biny_nn= get_acum_from_coord(lon,lat, data, nnear=50)

    info= plt.hist( binx_nn[0])
    plt.plot( lon[0], 2,'o')
    plt.savefig('hist')


if __name__ == '__main__':
    pass

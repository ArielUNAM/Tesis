import sys

from matplotlib.colors import Normalize
sys.path.append('../')

from src.pyRadar.dataPaths import *
from src.pyRadar.sections import *
import src.pyRadar.pyRadar as pr

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import pyart
import cartopy.crs as ccrs 
import cartopy.feature as cfeature
import re

trimestres= {'1':['01','02','03'], '2':['04','05','06'], '3':['07','08','09'], '4':['10','11','12'], }

tirm_to_month= {'01':'ENERO', '02':'FEBRERO','03':'MARZO','04':'ABRIL','05':'MAYO','06':'JUNIO','07':'JULIO','08':'AGOSTO','09':'SEPTIEMBRE','10':'OCTUBRE', '11':'NOVIEMBRE', '12':'DICIEMBRE'}

def annual_acumulation():
    years= pr.get_path_files( path2save, "\d{4}" )
    for year in years:
        acum= np.zeros( (360,921) )
        months= pr.get_path_files( year, "\d{2}")
        for month in months:
            files= pr.get_path_files( month, "radar_\d{4}_\d{2}.npz$")
            for file in files:
                data= np.load( file )
                acum+= data['data']
        np.savez_compressed( path2save + year  , data= acum)

def daily_acumulation( ):
    paths= pr.get_path_files( path2root, 'QRO_\d{4}' )
    for path in paths:
        files= pr.get_files_from_path( path )
        for month in files.keys():
            for day in month.keys():
                acum= pr.get_acum( files[month][day] )
                np.savez_compressed( path2save + path[-4:] + month + day, data= acum)

def monthy_acumulation():
    years= pr.get_path_files( path2save, "\d{4}" )
    for year in years:
        months= pr.get_path_files( year, "\d{2}")
        for month in months:
            acum= np.zeros( (360,921) )
            days= pr.get_path_files( month, "\d{2}")
            for day in days:
                files= pr.get_path_files( day, "radar_\d{4}_\d{2}_\d{2}.npz$")
                for file in files:
                    data= np.load( file )
                    acum+= data['data']
        np.savez_compressed( path2save + year + month , data= acum)

def to_radar():
    radar= pr.clear_radar( pr.get_radar( filename ) )

    years= pr.get_path_files( path2save, "\d{4}" )
    for year in years:
        months= pr.get_path_files( year, "\d{2}")
        for month in months:
            files= pr.get_path_files( month, "radar_\d{4}_\d{2}.npz$")
            for file in files:
                data= np.load( file )
                radar_str= pr.numpy_to_radar_dict( data, f"Acumulado mensual. {year}-{month}","Acumulación mensual", units='mm/h' )
                radar.add_field( f'ACUM_{month}', radar_str )
        files= pr.get_path_files( month, "radar_\d{4}.npz$")
        data= np.load( file[0] )
        radar_str= pr.numpy_to_radar_dict( data, f"Acumulado anual. {year}","Acumulación anual", units='mm/h' )
        radar.add_field( f'ACUM', radar_str )

        pr.pyart.io.write_cfradial( path2save + 'radar' + year + '.nc', radar )


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
            ax.add_feature(cfeature.COASTLINE)
            ax.add_feature(cfeature.OCEAN, facecolor='#CCFEFF')
            ax.add_feature(cfeature.LAKES, facecolor='#CCFEFF')
            ax.add_feature(cfeature.RIVERS, edgecolor='#CCFEFF')
            ax.add_feature(cfeature.LAND, facecolor='#FFE9B5')
            ax.add_feature(cfeature.STATES, edgecolor='black', zorder=10)
        except Exception as e:
            print(radar_subplots[i], i)
            print(f"Revisa {e}")
            continue

    
    plt.savefig(f"prueba{i}")
    
def plot_reflectivity():
    """Graficas de reflectividad
    """
    iris= pr.get_iris( filename )
    reflectivity= pr.get_reflectivity( iris )
    pr.plot_reflectivity( reflectivity, "Reflectividad", "equivalent reflectivity (dBZ)", path2fig + "refWL" )

    radar= pr.get_radar( filename )
    pr.plot_reflectivity( radar, "Reflectividad", "equivalent reflectivity (dBZ)", path2fig + "refPR",radarFrom=True )
    
def plot_clutter():
    """Graficas de la aplicación del filtro gabella
    """
    iris= pr.get_iris( filename )
    reflectivity= pr.get_reflectivity( iris )
    pr.plot_clutter( reflectivity, "Filtro Gabella para disminuir el ruido", path2fig+"gabellaWL")
 
def plot_pia():

    iris= pr.get_iris( filename )
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
    shape, rainfall= pr.est_rain_rate_z( filename  )
    pr.plot_reflectivity( rainfall, "LLuvia", "[mm h$^-1$]", path2fig + "rainfallWL" )

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

def generate_radar_acum_trim(trim=3):
    paths= pr.get_path_files( path2save, "201[0-9]" ) 
    
    for path in paths:
        files= pr.get_path_files( path+'/', 'qro_radar_acum')

        radar= pr.get_radar( files[0] )
        radar_subplots= list( radar.fields.keys() )

        base_radar= pr.clear_radar( pr.get_radar( filename ) )

        n= len(radar_subplots)
        m_acum= np.zeros((360,921), dtype=np.float64)
        for i in range( n ):
            m_acum+= radar.fields[ radar_subplots[i] ][ 'data' ].filled()
            if( (i+1) % trim == 0 ):
                radar_dic= pr.numpy_to_radar_dict( m_acum, f"Acumulado trimestral para {path[-4:]}",f'ACUM_TRI_{ (i+1)/3 }',"Precipitación acumulada [$mm h^-1$]")
                base_radar.add_field( f'ACUM_TRI_{ (i+1)/3 }', radar_dic )

                m_acum= np.zeros((360,921), dtype=np.float64)

        plot_radar_gen( base_radar, path2fig + "monthAcum"+path[-4:]+"PR", vmax=[100, 10, 100, 100])

def generate_radar_acum_year():
    
    paths= pr.get_path_files( path2save, "201[0-9]" )    
    
    base_radar= pr.clear_radar( pr.get_radar( filename ) )
    
    for path in paths:
        files= pr.get_path_files( path+'/', 'qro_radar_acum')
        radar= pr.get_radar( files[0] )

        radar= pr.get_radar( files[0] )
        radar_subplots= list( radar.fields.keys() )

        y_acum= np.zeros((360,921), dtype=np.float64)
        for month in radar_subplots:
            y_acum+= radar.fields[month]['data'].filled()

        radar_dic= pr.numpy_to_radar_dict( y_acum.astype(np.float64), f"Acumulado anual para {path[-4:]}",f'ACUM_QRO_{path[-4:]}',"Precipitación acumulada [$mm h^-1$]")

        base_radar.add_field( f'ACUM_QRO_{path[-4:]}', radar_dic )

    plot_radar_gen( base_radar, path2fig + "yearAcumPR" )

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
    iris_07_15= pr.get_iris( path_radar_07_15 )

    #Obtenemos la metadata
    r, az, coord= pr.get_metadata( iris_07_15 )
    data= pr.get_reflectivity( iris_07_15 )

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
    # display= pyart.graph.RadarMapDisplay( radar )
    # fig= plt.figure( figsize=(25,25))
    # n=3
    # projection = ccrs.LambertConformal(central_latitude=radar.latitude['data'][0], central_longitude=radar.longitude['data'][0])

    # plot(radar,display,fig,n,radar_subplots,projection,binx_nn,biny_nn)

    #Aca tengo una tupla de coordenadas y de valores para cada punto en la cercania del punto graficado
    for coor, gaug in zip( zip(lon,lat),radar_at_gages ):
        print(coor, "Acumulado: " ,sum(gaug))

def plot_general(radar,field,title,filename):
    display= pyart.graph.RadarMapDisplay( radar )
    fig= plt.figure( figsize=(25,25))
    projection = ccrs.LambertConformal(central_latitude=radar.latitude['data'][0], central_longitude=radar.longitude['data'][0])

    pr.plot_field( radar, field, display, fig, projection, title, path2fig + filename)

def plot_section(radar,field,title,filename):

    pr.plot_field_section( radar, field, display, fig, projection, title, path2fig + filename, lat_max= 19.8, lat_min= 22,lon_max= -100.9, lon_min= -98.9,n_blocks=25)

def plot_section_labels(radar,field,title,filename):
    display= pyart.graph.RadarMapDisplay( radar )
    fig= plt.figure( figsize=(25,25))
    projection = ccrs.LambertConformal(central_latitude=radar.latitude['data'][0], central_longitude=radar.longitude['data'][0])

    pr.plot_field_labels_section( radar, field, display, fig, projection, title, path2fig + filename)

def plot_section_points(radar,field,title,filename):
    display= pyart.graph.RadarMapDisplay( radar )
    fig= plt.figure( figsize=(25,25))
    projection = ccrs.LambertConformal(central_latitude=radar.latitude['data'][0], central_longitude=radar.longitude['data'][0])

    pr.plot_field_points_section( radar, field, display, fig, projection, title, path2fig + filename)

def plot_mensual():
    #Obtenemos directorios de los años
    dirs= pr.get_path_files( path2save, "\d{4}" )

    for year in dirs:
        file= pr.get_path_files( year + '/', "qro_radar*" )
    
        radar= pr.get_radar( file[0] )
        #radar= pr.get_acum_by_fields( radar, 'ACUM', f'Acumulado anual {year[-4:]}' )

        fields= radar.metadata['field_names'].split(', ')
        for field in fields:

            plot_general( radar, field, f'Acumulado mensual {year[-4:]}:{field}', f'{year[-4:]}_{field}.png')

            plot_section( radar, field, f'Acumulado mensual {year[-4:]}:{field}', f'{year[-4:]}_{field}_sect.png')

            plot_section_labels( radar, field, f'Acumulado mensual {year[-4:]}:{field}', f'{year[-4:]}_{field}_label.png')

            plot_section_points( radar, field, f'Acumulado mensual {year[-4:]}:{field}', f'{year[-4:]}_{field}_point.png')

def plot_anual():
    #Obtenemos directorios de los años
    dirs= pr.get_path_files( path2save, "\d{4}" )

    for year in dirs:
        file= pr.get_path_files( year + '/', "qro_radar*" )
    
        radar= pr.get_radar( file[0] )
        radar.add_field( 'ZEROS', pr.numpy_to_radar_dict(np.zeros((360,921) ), 'aaa') )

        #radar= pr.get_acum_by_fields( radar, 'ACUM', f'Acumulado anual {year[-4:]}' )

        #plot_general( radar, 'ACUM', f'Acumulado anual {year[-4:]}', f'{year[-4:]}.png')

        plot_section( radar, 'ZEROS', 'prueba','prueba')

        #plot_section_labels( radar, 'ACUM', f'Acumulado anual {year[-4:]}', f'{year[-4:]}_label.png',n_blocks=15)

        #plot_section_points( radar, 'ACUM', f'Acumulado anual {year[-4:]}', f'{year[-4:]}_point.png',n_blocks=15)


def plot_config( radar ):
    display= pyart.graph.RadarMapDisplay( radar )
    fig= plt.figure( figsize=(25,25))
    projection = ccrs.LambertConformal(central_latitude=radar.latitude['data'][0], central_longitude=radar.longitude['data'][0])

    return display, fig, projection

def plot_clear():
    plt.cla()
    plt.clf()

def plot_grid( radar, field, display, fig, projection, title, filename ):
    a,b= pr.plot_field_labels_acum_section( radar, field, display, fig, projection, title, filename )
    pr.plot_heat_map( a, filename+'_map' )

    return sum(a)

def print_acum( data, segmentos ): 
    
    segmentos= [re.findall( 'segmento_\d{1}', x ) for x in dir(config1)]
    segmentos= [item for sublist in segmentos for item in sublist]

    acums= {}
    for segmento in segmentos:
        #P1,P2,P3,P4= config3.segmento_1()
        P1,P2,P3,P4= getattr( config1, segmento )()
        d_acum,_,_= pr.get_acum_from_rect( P1,P2,P3,P4,10,data )
        acums[segmento]= d_acum
    
    print( acums )


if __name__ == '__main__':
#    plot_anual()
    
    year= '2017'
    filename= f"/home/arielcg/Documentos/Tesis/src/data/radar/{year}/qro_radar_acum.cn"
    radar= pr.get_radar( filename )

    data= np.zeros((360,921))

    
    fields= radar.metadata['field_names'].split(', ')
    for field in fields:
        data+= radar.fields[field]['data'].filled()

    radar.add_field( 'ACUM', pr.numpy_to_radar_dict( data, f'Acumulación anual ({year})','Acumulado','mm/h') )

    display, fig, projection= plot_config( radar )    

    ax= fig.add_subplot( 1,1,1, projection= projection )

    # #Radar coords
    lon_0, lat_0= pr.get_coords( radar )

    lat_max= 19.8; lat_min= 21.7
    lon_max= -100.59; lon_min= -99.0
    

    # #Lines
    lat_lines=np.linspace(lat_min, lat_max, 10)
    lon_lines=np.linspace(lon_min, lon_max, 10)

    #Plotting
    display.plot_ppi_map( 'ACUM',
                          lat_0= lat_0,
                          lon_0= lon_0,
                          max_lat=lat_max, min_lat=lat_min,
                          max_lon=lon_max, min_lon=lon_min,
                          lat_lines= lat_lines,
                          lon_lines= lon_lines,
                          resolution= '10m',
                          vmin= 0, vmax= 200,
                          projection= projection,
                          fig= fig, ax= ax,
                          cmap= cm.get_cmap('GnBu'),
                          #colorbar_flag=False
                        )
    display.plot_point(lon_0, lat_0,label_text='Radar')

    # #Axis
    ax.xaxis.set_tick_params(rotation=35)
    ax.set_aspect("equal")

    segmentos= [re.findall( 'segmento_\d{1}', x ) for x in dir(config3)]
    segmentos= [item for sublist in segmentos for item in sublist]

    for segmento in segmentos:
        P1,P2,P3,P4, n_points= getattr( config3, segmento )()

        y= lambda m,b,x: m*x + b
        x= lambda m,b,y: (y-b)/m
        
        m,b= pr.get_m_b( P1, P2 )
        Y1= np.linspace( P1[1], P2[1],n_points)
        F1= [ ( x(m,b,j), j ) for j in Y1]

        m,b= pr.get_m_b( P3, P4 )
        Y2= np.linspace( P3[1], P4[1],n_points)
        F2= [ ( x(m,b,j), j ) for j in Y2]
        
        M= []
        #Vamos a generar lineas para cada punto
        for l1, l2 in zip( F1, F2 ):
            X= np.linspace( l1[0], l2[0], n_points )
            m,b= pr.get_m_b( l1, l2 )
            M.append( [ 
                [ round(i, ndigits=4) for i in X ],
                [ round(y(m,b,i),ndigits=4) for i in X ]
            ] )

        g_labels= []
        g_coords= []
        for coords in M:
            radar_at_gages,x,y,_,_,_,_= pr.get_acum_from_coord(coords[0],coords[1], data, nnear=1)
            labels= []
            coordinates= []
            for coor, gaug in zip( zip(coords[0],coords[1]),radar_at_gages ):
                #print(coor, "Acumulado: " ,sum(gaug) if type(gaug) is list else gaug )
                labels.append( sum(gaug) if type(gaug) is list else gaug )
                coordinates.append( coor )
            pr.plot_point( display, coordinates)
            #print( coordinates, ':', labels )
            g_labels.append( labels )
            g_coords.append( coordinates )

        i= 0
        acum= 0
        for label in g_labels:
            acum+= sum(label)
            i+= 1

    print(year + 'acum:', acum)
    #savefig
    plt.savefig( path2fig +year+ '_config3' )
    

def trim_plot():
    year= '2017'
    filename= f"/home/arielcg/Documentos/Tesis/src/data/radar/{year}/qro_radar_acum.cn"
    radar= pr.get_radar( filename )

    fields= radar.metadata['field_names'].split(', ')

    d_acum= {}
    for key, value in trimestres.items():
        acum= np.zeros( (360,921) )
        flag= 0
        for field in fields:
            if ( field[-2:] in value ):
                flag+= 1
                acum+= radar.fields[ field ]['data'].filled()
                
        if flag > 0:
            
            radar.add_field( f'trim_{key}', pr.numpy_to_radar_dict( acum, f'Acumulado_anual ({year})', f'ACUM_{year}', 'mm/h' ) )



            display, fig, projection= plot_config( radar )

            plot_clear()

            pr.plot_field( radar,  f'trim_{key}' , display, fig, projection, f'trim_{key}', path2fig + year + '_' + f'trim_{key}' )

            plot_clear()

            pr.plot_field_section( radar,  f'trim_{key}' , display, fig, projection, f'trim_{key}' + '_sec', path2fig + year + '_' + f'trim_{key}' + '_sec' )

            plot_clear()

            s= plot_grid( radar,  f'trim_{key}' , display, fig, projection, f'trim_{key}' + '_vals', path2fig + year + '_' + f'trim_{key}' + '_vals' )

            d_acum[f'trim_{key}']= s

    df= pd.DataFrame.from_dict( data=d_acum, orient='index' ).to_csv( path2csv + f'trim_{key}' + year + '.csv', index=False )



def all_plot(year):

    filename= f"/home/arielcg/Documentos/Tesis/src/data/radar/{year}/qro_radar_acum.cn"
    radar= pr.get_radar( filename )

    fields= radar.metadata['field_names'].split(', ')

    d_acum= {}
    acum= np.zeros( (360,921) )
    for field in fields:

        display, fig, projection= plot_config( radar )

        acum+= radar.fields[ field ]['data'].filled()

        pr.plot_field( radar,  field , display, fig, projection, field, path2fig + year + '_' + field )

        plot_clear()

        pr.plot_field_section( radar,  field , display, fig, projection, field + '_sec', path2fig + year + '_' + field + '_sec' )

        plot_clear()

        s= plot_grid( radar,  field , display, fig, projection, field + '_vals', path2fig + year + '_' + field + '_vals' )

        d_acum[ field ]= s

    radar.add_field( 'ACUM', pr.numpy_to_radar_dict( acum, f'Acumulado_anual ({year})', f'ACUM_{year}', 'mm/h' ) )

    plot_clear()
    
    pr.plot_field( radar,  'ACUM' , display, fig, projection, year, path2fig + year )

    plot_clear()

    pr.plot_field_section( radar,  'ACUM' , display, fig, projection, year + '_sec', path2fig + year + '_sec' )

    plot_clear()

    s= plot_grid( radar,  'ACUM' , display, fig, projection, year + '_vals', path2fig + year + '_vals' )

    pd.DataFrame.from_dict( data=d_acum, orient='index' ).to_csv( path2csv + year + '.csv', index=False )


def aux2():
    filename= "/home/arielcg/Documentos/Tesis/src/data/radar/2015/qro_radar_acum.cn"
    radar= pr.get_radar( filename )

    #plot_bins(binx,biny,binx_nn,biny_nn,x,y)
    display= pyart.graph.RadarMapDisplay( radar )
    fig= plt.figure( figsize=(25,25))
    projection = ccrs.LambertConformal(central_latitude=radar.latitude['data'][0], central_longitude=radar.longitude['data'][0])

    fields= radar.metadata['field_names'].split(', ')
    acum= np.zeros( (360,921) )

    for field in fields:
        acum+= radar.fields[field]['data'].filled()
    
    radar.add_field( 'ACUM', pr.numpy_to_radar_dict(
        np.zeros((360,921)),
        'Acumulado anual 2015',
        'ACUM ANUAL',
        'mm/h') )

    # pr.plot_field( radar, 'ACUM', display, fig, projection, "Prueba de funcion", "prueba1" )
    # pr.plot_field_section( radar, 'ACUM', display, fig, projection, "Prueba de funcion", "prueba2" )
    # pr.plot_field_points_section( radar, 'ACUM', display, fig, projection, "Prueba de funcion", "prueba3" )
    #pr.plot_field_labels_section( radar, 'ACUM', display, fig, projection, "Prueba de funcion", "prueba4" )
    gages, mp= pr.plot_field_labels_acum_section( radar, 'ACUM', display, fig, projection, "Prueba de funcion", "prueba4" )
    pr.plot_heat_map( gages, 'prueba4_heat' )


def aux():
    filename= "/home/arielcg/Documentos/Tesis/src/data/radar/2015/qro_radar_acum.cn"
    radar= pr.get_radar( filename )

    #plot_bins(binx,biny,binx_nn,biny_nn,x,y)
    display= pyart.graph.RadarMapDisplay( radar )
    fig= plt.figure( figsize=(25,25))
    projection = ccrs.LambertConformal(central_latitude=radar.latitude['data'][0], central_longitude=radar.longitude['data'][0])

    fields= radar.metadata['field_names'].split(', ')
    acum= np.zeros( (360,921) )

    for field in fields:
        acum+= radar.fields[field]['data'].filled()
    
    radar.add_field( 'ACUM', pr.numpy_to_radar_dict(
        acum,
        'Acumulado anual 2015',
        'ACUM ANUAL',
        'mm/h') )

    # pr.plot_field( radar, 'ACUM', display, fig, projection, "Prueba de funcion", "prueba1" )
    # pr.plot_field_section( radar, 'ACUM', display, fig, projection, "Prueba de funcion", "prueba2" )
    # pr.plot_field_points_section( radar, 'ACUM', display, fig, projection, "Prueba de funcion", "prueba3" )
    gages, mp= pr.plot_field_labels_section( radar, 'ACUM', display, fig, projection, "Prueba de funcion", "prueba4" )

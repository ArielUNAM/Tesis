import sys

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
import cv2
from os import remove


trimestres= {'1':['01','02','03'], '2':['04','05','06'], '3':['07','08','09'], '4':['10','11','12'], }

tirm_to_month= {'01':'ENERO', '02':'FEBRERO','03':'MARZO','04':'ABRIL','05':'MAYO','06':'JUNIO','07':'JULIO','08':'AGOSTO','09':'SEPTIEMBRE','10':'OCTUBRE', '11':'NOVIEMBRE', '12':'DICIEMBRE'}

# Verificados
# ==============
def plot_config( radar ):
    display= pyart.graph.RadarMapDisplay( radar )
    fig= plt.figure( figsize=(25,25))
    projection = ccrs.LambertConformal(central_latitude=radar.latitude['data'][0], central_longitude=radar.longitude['data'][0])

    return display, fig, projection

def plot_clear():
    plt.cla()
    plt.clf()

def plot( radar, field, conf, title, filename ):
    plot_clear()
    pr.plot_field( radar, field, conf[0], conf[1], conf[2], title, filename +'_' + field )
    
    plot_clear()
    pr.plot_field_section( radar, field, conf[0], conf[1], conf[2], title, filename +'_sec_' + field )

    plot_clear()
    s= plot_grid( radar, field, conf[0], conf[1], conf[2], title, filename + '_sec_vals_' + field )

    img_over_post(filename +'_sec_vals_' + field +'.png',filename + '_sec_vals_' + field + '_map.png', filename +'_'+ field+'_map')

    remove(filename + '_sec_vals_' + field +'.png')
    
    remove(filename + '_sec_vals_' + field + '_map'+'.png')

    return s

def plot_reflectivity():
    """Graficas de reflectividad (check)
    """
    iris= pr.get_iris( filename )
    reflectivity= pr.get_reflectivity( iris )
    pr.plot_reflectivity( reflectivity, "Reflectividad", "Reflectividad equivalente (dBZ)", path2fig + "refWL" )

    radar= pr.get_radar( filename )
    pr.plot_reflectivity( radar, "Reflectividad", "Reflectividad equivalente  (dBZ)", path2fig + "refPR",radarFrom=True )
    
def plot_clutter():
    """Graficas de la aplicación del filtro gabella
    """
    iris= pr.get_iris( filename )
    reflectivity= pr.get_reflectivity( iris )
    pr.plot_clutter( reflectivity, "Filtro Gabella para disminuir el ruido", path2fig+"gabellaWL")
 
def plot_inter():
    iris= pr.get_iris( filename )
    reflectivity= pr.get_reflectivity( iris )
    data_no_clutter= pr.clutter_processing( reflectivity )
    pr.plot_reflectivity( data_no_clutter, 'Interpolación', "Reflectividad equivalente  (dBZ)", path2fig + "intWL" )

def plot_pia():

    iris= pr.get_iris( filename )
    reflectivity= pr.get_reflectivity( iris )

    #beam= ([0,-860],[0,-280]) #Get this values manually
    beam= ([0,-680],[0,680]) #Get this values manually
    mybeams= slice(250, 255) #This is an angle, get manually

    #First plot
    pr.plot_beam( reflectivity, beam, "Sección del radar analizada", "equivalent reflectivity (dBZ)", path2fig+"beamWL" )

    #Pia plots
    pr.plot_attenuation( reflectivity, mybeams, path2fig+"kreamerWL", ylim=1)

    pr.plot_attenuation( reflectivity, mybeams, path2fig+"harrisonhWL",pia_title="PIA according to Hitchfeld and Bordan",beams_title="PIA according to Hitchfeld and Bordan", type="hitchfeld", ylim=1)

    pr.plot_attenuation( reflectivity, mybeams, path2fig+"mkreamerWL",pia_title="PIA according to Kraemer modificado",beams_title="PIA according to Kraemer modificado", type="mkraemer",ylim=1 )

    pr.plot_attenuation( reflectivity, mybeams, path2fig+"harrisonWL",pia_title="PIA according to Harrison",beams_title="PIA according to Harrison", type="harrison", ylim=7)

def plot_acum():
    rainfall= pr.est_rain_rate_z( filename  )
    pr.plot_reflectivity( rainfall, "Precipitación", "Precipitación equivalente $[mm/h]$", path2fig + "rainfallWL" )

def plot_trims():
    #Define si lo quieres en el mismo radar o en otros
    files= pr.get_path_files( path2save, "radar_201\d{1}", is_dir=False ) 

    trimestres= ['Trimestre 1', 'Trimestre 2', 'Trimestre 3', 'Trimestre 4']

    for file in files:
        radar= pr.get_radar( file )
        conf= plot_config( radar )
        d_acum= {}
        for trim in trimestres:
            s= plot( radar, trim, conf, f"Acumulación del trimestre {trim}", path2fig + file[-7:-3] )

            d_acum[ trim ]= s

        pd.DataFrame.from_dict( data=d_acum, orient='index' ).to_csv( file[-7:-3] + '_trim' + '.csv')

def plot_anual():
    #Define si lo quieres en el mismo radar o en otros
    files= pr.get_path_files( path2save, "radar_201\d{1}", is_dir=False ) 

    d_acum= {}
    for file in files:
        radar= pr.get_radar( file )
        conf= plot_config( radar )

        s= plot( radar, 'ACUM', conf, f"Acumulación del anual {file[-7:-3]}", path2fig + file[-7:-3] )

        d_acum[ file[-7:-3] ]= s

    pd.DataFrame.from_dict( data=d_acum, orient='index' ).to_csv( 'Anual' + '.csv')

def img_over_post(f1,f2,filename):
    img1= cv2.imread(f1)
    img2= cv2.imread(f2)

    dst= cv2.addWeighted(img1, 0.4, img2, 0.3, 0)
    
    cv2.imwrite( filename + '.png', dst )

def daily_acumulation( ):
    #Get a list with dir paths where data are.
    #paths= pr.get_path_files( path2root, 'QRO_\d{4}' )
    paths= pr.get_path_files( path2root, 'QRO_2016' )

    #For dir in dirPaths
    for path in paths:
        print(path[-4:])
        #Get all files from dirPath. The result is a dic where the key is the month and value is another dic where the key is the dat
        files= pr.get_files_from_path( path )
        #The neted loop allow us to get each file
        for month in files.keys():
            print("Month: ", month)
            for day in files[ month ].keys():
                #Get the acum from a day and save in a compres file
                acum= pr.get_acum( files[month][day] )
                np.savez_compressed( path2save + path[-4:] + '/'+ month + '/'+  path[-4:]+month +day, data= acum)

def monthy_acumulation():
    max_value= 100000
    
    years= pr.get_path_files( path2save, "\d{4}" )
    for year in years:
        print(year[-4:])
        months= pr.get_path_files( year + '/', "\d{2}")
        
        for month in months:
            acum= np.zeros( (360,921) )
            days= pr.get_path_files( month + '/', "\d{8}.npz$", is_dir=False)

            for file in days:
                data= np.load( file )

                new_data= np.where( data['data'] < max_value, data['data'], 0)

                acum+= new_data
            np.savez_compressed( path2save + year[-4:] + '/'+  year[-4:]+ month[-2:] , data= acum)

def annual_acumulation():
    years= pr.get_path_files( path2save, "\d{4}" )
    #years= pr.get_path_files( path2save, "2017" )
    for year in years:
        print(year[-4:])
        radar= pr.clear_radar( pr.get_radar( filename ) )
        acum= np.zeros( (360,921) )
        months= pr.get_path_files( year + '/', "\d{6}.npz$", is_dir=False)
        for file in months:
            data= np.load( file )
            acum+= data['data']
            radar.add_field( f'ACUM_{file[-6:-4]}', 
                pr.numpy_to_radar_dict( 
                    data['data'],
                    'Precipitación mensual estimada', 
                    'Precipitación estimada [$mm/h$]', 'mm/h' )
                    )
        radar.add_field( 'ACUM', 
                pr.numpy_to_radar_dict( 
                    acum,
                    'Precipitación anual estimada', 
                    'Precipitación estimada [$mm/h$]', 'mm/h' )
                    )
        pr.pyart.io.write_cfradial( path2save + 'radar_' + year[-4:] + '.nc', radar )
    
def generate_radar_acum_trim():
    #Define si lo quieres en el mismo radar o en otros
    files= pr.get_path_files( path2save, "radar_201\d{1}", is_dir=False ) 
    
    for file in files:
        print(file[-7:-3])
        radar= pr.get_radar( file )
        fields= pr.get_all_fields( radar )

        for trim, values in trimestres.items():
            trim_fields= [field for field in fields if field[-2:] in values ]
            acum= np.zeros((360, 921))

            for field in trim_fields:
                try:
                    acum+= radar.fields[ field ]['data'].filled()
                except:
                    acum+= radar.fields[ field ]['data']
            radar.add_field( f"TRIM_{trim}",
            pr.numpy_to_radar_dict( acum,
                "Precipitación acumulada para el trimestre {trim}", 
                "Precipitación equivalente",
                'mm/h') )
        pr.pyart.io.write_cfradial( path2save + 'radar_' + file[-7:-3] + '.nc', radar )  

def plot_grid( radar, field, display, fig, projection, title, filename ):
    a,_= pr.plot_field_labels_acum_section( radar, field, display, fig, projection, title, filename )
    pr.plot_heat_map( a, filename + '_map' )

    return sum(a)

def monthy_csv():
    #Define si lo quieres en el mismo radar o en otros
    files= pr.get_path_files( path2save, "radar_201\d{1}", is_dir=False ) 

    for file in files:
        print(file[-7:-3])
        radar= pr.get_radar( file )
        fields= pr.get_all_fields( radar )
        conf= plot_config( radar ) 

        d_acum= {}
        for field in fields:
            print(field)
            d_acum[ field ]= sum( pr.plot_field_labels_acum_section( radar, field, conf[0], conf[1], conf[2], f'Acumulación del mes { field[-2:] }', filename )[0] )

        pd.DataFrame.from_dict( data=d_acum, orient='index' ).to_csv( file[-7:-3]+'_mensual' + '.csv')

def get_configs( config ):
    segmentos= [re.findall( 'segmento_\d{1}', x ) for x in dir( config )]
    return [item for sublist in segmentos for item in sublist]

def get_init_lines( P1, P2, P3, P4, n_points ):
    x= lambda m,b,y: (y-b)/m
    
    m1,b1= pr.get_m_b( P1, P2 )
    Y1= np.linspace( P1[1], P2[1],n_points)
    
    m2,b2= pr.get_m_b( P3, P4 )
    Y2= np.linspace( P3[1], P4[1],n_points)

    return  [ ( x(m1,b1,j), j ) for j in Y1], [ ( x(m2,b2,j), j ) for j in Y2]

def get_lines( I1, I2, n_points ):
    y= lambda m,b,x: m*x + b

    M= []
    for l1, l2 in zip( I1, I2 ):
        X= np.linspace( l1[0], l2[0], n_points )
        m,b= pr.get_m_b( l1, l2 )
        M.append( [ 
            [ round(i, ndigits=4) for i in X ],
            [ round(y(m,b,i),ndigits=4) for i in X ]
                ] )
    return M

def get_M( config ):
    P1,P2,P3,P4, n_points= getattr( config3, config )
    I1, I2= get_init_lines(P1,P2, P3, P4, n_points)
    return get_lines( I1, I2, n_points )

def get_M_coords( M ):
    l_coords= []
    for coords in M:
        for coor in zip(coords[0], coords[1]):
            l_coords.append( coor )
    return l_coords
        
def get_acum_seg( M, data, nnear ):
    
    g_values= []
    for coords in M:
        radar_at_gages,_,_,_,_,_,_= pr.get_acum_from_coord(coords[0],coords[1], data, nnear=nnear)

        inner_values= []
        for gaug in radar_at_gages:
            inner_values.append( sum(gaug) if type(gaug) is list else gaug )
        g_values.append( inner_values )

    return g_values
    #pandas.DataFrame(data=None, index=None, columns=None, dtype=None, copy=None)

def monthy_seg_csv():
    files= pr.get_path_files( path2save, "radar_201\d{1}", is_dir=False ) 

    configurations= get_configs( config1 )
    nnear= 1

    d_acum= {}
    for file in files:
        radar= pr.get_radar( file )
        fields= pr.get_all_fields( radar )
        for field in fields:
            vals= 0
            for config in configurations:
                M= get_M( config )
                try:
                    #Obtenemos la informacion
                    data= radar.fields[ field ]['data'].filled()
                except:
                    data= radar.fields[ field ]['data']
                vals+= sum( get_acum_seg( M, data, nnear ) )
            d_acum[ field ]= vals

        pd.DataFrame.from_dict( data=d_acum, orient='index' ).to_csv( file[-7:-3]+f'_mensual_{config1}' + '.csv')

def anual_seg_csv():
    pass

def locations_csv():
    pass
# No Verificados
# ==============

def plot_seg():
    #Reducir
    year= '2017'
    filename= f"/home/arielcg/Documentos/Tesis/src/data/radar/radar_{year}.nc"
    radar= pr.get_radar( filename )
    data= np.zeros((360,921))

    display, fig, projection= plot_config( radar )    

    pr.plot_field_section( radar, 'ACUM', display, fig, projection, f'Acumulado anual ({year})',f"{year}_segmento",savefig=False)

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


def acum_csv():
#    plot_anual()
    files= pr.get_path_files( path2save, 'radar_\d{4}\.nc$', is_dir=False )
    n_points= 15
    nnear= 1

    for file in files:
        radar= pr.get_radar( file )

        fields= pr.get_all_fields( radar )
        #Define space 
        lat_max= 19.8; lat_min= 21.7
        lon_max= -100.59; lon_min= -99.0
    
        # #Lines
        lat_lines=np.linspace(lat_min, lat_max, n_points)
        lon_lines=np.linspace(lon_min, lon_max, n_points)

        #data= pr.get_acum_from_fields( radar, fields )
        acum= {}
        for field in fields:
            data= radar.fields[ field ]['data'].filled()
        

            mp= pr.get_middle_points( lon_lines, lat_lines )

            lon= [ point[0] for point in mp ]
            lat= [ point[1] for point in mp ]

            radar_at_gages= pr.get_acum_by_gages( lon, lat, data, nnear)
            gages= [ gage for gage in radar_at_gages ]

            acum[field]= sum(gages)

        pd.DataFrame.from_dict( data=acum, orient='index' ).to_csv( file[-7:-3] + '.csv')#, index=False )


def acum_from_files(): 
    import json
    years= ['2015', '2016', '2017']
    #n_points= 15
    nnear= 4
    files= pr.get_path_files( "/home/arielcg/Documentos/Tesis/src/data/base/", ".*\.csv$" )
    for file in files:
        df= pd.read_csv( file )
        lon = df.Longitude.to_list()
        lat= df.Latitude.to_list()
        for year in years:
            print(year)
            filename= f"/home/arielcg/Documentos/Tesis/src/data/radar/{year}/qro_radar_acum.cn"

            radar= pr.get_radar( filename )
            fields= pr.get_all_fields( radar )    
            
            acum= {}
            for field in fields:
                data= radar.fields[ field ]['data'].filled()

                radar_at_gages= pr.get_acum_by_gages( lon, lat, data, nnear)
                gages= [ gage for gage in radar_at_gages ]

                
                vals= []
                coordss= []
                for gage, coords in zip( gages, zip(lon,lat) ):
                    vals.append(sum(gage))
                    coordss.append(coords)
                acum[field]= [ coordss, vals ]
            
            write_file= open(year + file[-10:]+".json", "w")
            json.dump(acum, write_file)
            write_file.close()
            
        # a_file = open("data.json", "r")
        # output = a_file.read()
        # pd.DataFrame.from_dict( data=acum, orient='index' ).to_csv( year + file[-10:]+ '.csv')
def data_sections():
    years= ['2015', '2016', '2017']
    #n_points= 15
    nnear= 1
    for year in years:
        print(year)
        filename= f"/home/arielcg/Documentos/Tesis/src/data/radar/{year}/qro_radar_acum.cn"

        radar= pr.get_radar( filename )

        fields= pr.get_all_fields( radar )

        segmentos= [re.findall( 'segmento_\d{1}', x ) for x in dir(config1)]
        segmentos= [item for sublist in segmentos for item in sublist]

        d_acum= {}
        for field in fields:
            data= radar.fields[ field ]['data'].filled()
            acum= 0
            for segmento in segmentos:
                P1,P2,P3,P4, n_points= getattr( config1, segmento )()
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

                for coords in M:
                    radar_at_gages= pr.get_acum_by_gages( coords[0],coords[1], data, nnear)
                    gages= [ gage for gage in radar_at_gages ]
                    acum+= sum(gages)

            d_acum[field]= acum
        pd.DataFrame.from_dict( data=d_acum, orient='index' ).to_csv( year + 'config1'  + '.csv')   
                

def acum_csv():
#    plot_anual()
    years= ['2015', '2016', '2017']
    n_points= 15
    nnear= 1
    for year in years:
        filename= f"/home/arielcg/Documentos/Tesis/src/data/radar/{year}/qro_radar_acum.cn"

        radar= pr.get_radar( filename )

        fields= pr.get_all_fields( radar )
        #Define space 
        lat_max= 19.8; lat_min= 21.7
        lon_max= -100.59; lon_min= -99.0
    
        # #Lines
        lat_lines=np.linspace(lat_min, lat_max, n_points)
        lon_lines=np.linspace(lon_min, lon_max, n_points)

        #data= pr.get_acum_from_fields( radar, fields )
        acum= {}
        for field in fields:
            data= radar.fields[ field ]['data'].filled()
        

            mp= pr.get_middle_points( lon_lines, lat_lines )

            lon= [ point[0] for point in mp ]
            lat= [ point[1] for point in mp ]

        

            radar_at_gages= pr.get_acum_by_gages( lon, lat, data, nnear)
            gages= [ gage for gage in radar_at_gages ]

            acum[field]= sum(gages)

        pd.DataFrame.from_dict( data=acum, orient='index' ).to_csv( year + '.csv')#, index=False )

        #gages= [ round(sum(gage)) if round(sum(gage)) < max_val else max_val for gage in gages ]
        #gages= [ round(sum(gage)) for gage in gages ]
        # n= int(np.sqrt( len(gages) ))
        # m_gages= np.rot90(np.reshape( gages, (n,n)), 3 )
        
        # plt.imshow( m_gages )
        # plt.savefig("pureba1")

        # x,y= np.where( m_gages < 80 )
        # for i, j in zip(x,y):
        #     m_gages[i][j]= sum(pr.get_vn_neig( m_gages, (i,j) ))/4
        # plot_clear()
        # plt.imshow( m_gages )
        # plt.savefig("pureba2")
        


    

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

if __name__ == '__main__':
    #plot_trims()
    #plot_anual()
    #monthy_csv()
    plot_seg()

    # #acum_csv()
    # radar= pr.get_radar( '/home/arielcg/Documentos/Tesis/src/data/radar/radar_2015.nc' )
    
    # fields= radar.fields.keys()
    # configs= plot_config( radar )
    # for field in fields:
    #     plot_clear()
    #     pr.plot_field( radar, field, configs[0],configs[1],configs[2],  "Precipitación equivalente acumulada", path2fig + field)
    

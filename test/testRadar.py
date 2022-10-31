import sys
sys.path.append('../')

from src.pyRadar.dataPaths import *
from src.pyRadar.sections import *
import src.pyRadar.pyRadar as pr

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import cv2
from os import remove


trimestres= {'1':['01','02','03'], '2':['04','05','06'], '3':['07','08','09'], '4':['10','11','12'], }

tirm_to_month= {'01':'ENERO', '02':'FEBRERO','03':'MARZO','04':'ABRIL','05':'MAYO','06':'JUNIO','07':'JULIO','08':'AGOSTO','09':'SEPTIEMBRE','10':'OCTUBRE', '11':'NOVIEMBRE', '12':'DICIEMBRE'}

# Verificados
# ==============
def plot_config( radar ):
    display= pr.pyart.graph.RadarMapDisplay( radar )
    fig= plt.figure( figsize=(10,8))
    projection = pr.ccrs.LambertConformal(central_latitude=radar.latitude['data'][0], central_longitude=radar.longitude['data'][0])

    return display, fig, projection

def plot_clear():
    plt.cla()
    plt.clf()

def plot( radar, field, conf, title, filename, colorbar_flag=True ):
    #Entire radar plot
    plot_clear()
    pr.plot_field( radar, field, conf[0], conf[1], conf[2], title, filename +'_' + field, colorbar_flag=colorbar_flag)
    
    plot_clear()
    pr.plot_field_section( radar, field, conf[0], conf[1], conf[2], title, filename +'_sec_' + field, colorbar_flag=colorbar_flag )

    plot_clear()
    s= plot_grid( radar, field, conf[0], conf[1], conf[2], title, filename + '_sec_vals_' + field )

    #img_over_post(filename +'_sec_vals_' + field +'.png',filename + '_sec_vals_' + field + '_map.png', filename +'_'+ field+'_map')

    #remove(filename + '_sec_vals_' + field +'.png')
    
    #remove(filename + '_sec_vals_' + field + '_map'+'.png')

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
    pr.plot_reflectivity( rainfall, "Precipitación", "Precipitación equivalente $[mm]$", path2fig + "rainfallWL" )

def plot_trims(CSV_files=True):
    #Define si lo quieres en el mismo radar o en otros
    files= pr.get_path_files( path2save, "radar_201\d{1}", is_dir=False ) 

    trimestres= ['Trimestre 1', 'Trimestre 2', 'Trimestre 3', 'Trimestre 4']

    colorbar_flag= True

    for file in files:
        radar= pr.get_radar( file )
        conf= plot_config( radar )
        d_acum= {}
        for trim in trimestres:
            s= plot( radar, trim, conf, f"Acumulación del  {trim}", path2fig + file[-7:-3], colorbar_flag=colorbar_flag )
            colorbar_flag= colorbar_flag if not colorbar_flag else False

            d_acum[ trim ]= s
        if( CSV_files ):
            pd.DataFrame.from_dict( data=d_acum, orient='index' ).to_csv( file[-7:-3] + '_trim' + '.csv')

def plot_anual(to_csv=True):
    #Define si lo quieres en el mismo radar o en otros
    files= pr.get_path_files( path2save, "radar_201\d{1}", is_dir=False ) 

    colorbar_flag= True

    d_acum= {}
    for file in files:
        radar= pr.get_radar( file )
        conf= plot_config( radar )

        s= plot( radar, 'ACUM', conf, f"Acumulación del anual {file[-7:-3]}", path2fig + file[-7:-3], colorbar_flag=colorbar_flag )

        d_acum[ file[-7:-3] ]= s

        colorbar_flag= colorbar_flag if not colorbar_flag else False
        

    if( to_csv ):
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
    years= pr.get_path_files( path2save, "x\d{4}" )
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
                    'Precipitación estimada [$mm$]', 'mm' )
                    )
        radar.add_field( 'ACUM', 
                pr.numpy_to_radar_dict( 
                    acum,
                    'Precipitación anual estimada', 
                    'Precipitación estimada [$mm$]', 'mm' )
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
                'mm') )
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
    P1,P2,P3,P4, n_points= getattr( config3, config )()
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

def seg_csv():
    files= pr.get_path_files( path2save, "radar_201\d{1}", is_dir=False ) 

    configurations= get_configs( config3 )
    nnear= 1

    d_acum= {}
    for file in files:
        print(file[-7:-3])
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
                
                vals+= sum( [ sum( acum ) for acum in 
                    get_acum_seg( M, data, nnear ) ])
            d_acum[ field ]= vals

        pd.DataFrame.from_dict( data=d_acum, orient='index' ).to_csv( file[-7:-3]+'_mensual_config3' + '.csv')

def locations_csv():
    files= pr.get_path_files( "/home/arielcg/Documentos/Tesis/src/data/base/", ".*\.csv$", is_dir=False )
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

def acum_annual_from_files(): 
    years= ['2015', '2016', '2017']
    nnear= 2
    files= pr.get_path_files( "/home/arielcg/Documentos/Tesis/src/data/base/", ".*\.csv$" , is_dir=False)
    
    for file in files:
        
        df= pd.read_csv( file )
        lon = df.Longitude.to_list()
        lat= df.Latitude.to_list()
        for year in years:
            print(year)
            filename= f"/home/arielcg/Documentos/Tesis/src/data/radar/radar_{year}.nc"

            radar= pr.get_radar( filename )
            fields= pr.get_all_fields( radar )    
            
            for field in fields:
                data= radar.fields[ field ]['data'].filled()

                radar_at_gages= pr.get_acum_by_gages( lon, lat, data, nnear)
                gages= [ gage for gage in radar_at_gages ]

                df[field +'_'+ year]= [ sum(gage) if type( gages ) is list else gage for gage in gages ]
                
        df.to_csv( file[:-4]+ '_process' + '.csv' )


if __name__ == '__main__':
    #acum_annual_from_files()
    #plot_trims(False)
    plot_anual(False)

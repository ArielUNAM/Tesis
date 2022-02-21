import sys
sys.path.append('../')

import src.pyRadar.pyRadar as pr

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pyart
import cartopy.crs as ccrs

path2root= "/home/arielcg/"
path2save= "/home/arielcg/Documentos/Tesis/src/data/radar/"
path2fig= '/home/arielcg/Documentos/Tesis/src/data/img/'

dict2data= {'2015':'QRO_2015/','2016':'QRO_2016/','2017':'QRO_2017/'}

def main():  
    #acum_month()
    # for year in dict2data.keys():
    #     path= path2save+year
    #     filename= path + '/QRO_ACUM_{}'.format(year)
    #     pr.rada
    ploter= pr.radar_manipulator()

    ploter.plot_geo_ppi_art("/home/arielcg/Documentos/Tesis/src/data/radar/2015/QRO_ACUM_2015.nc")
    #ploter.plot_rain_gauge_locations("/home/arielcg/Documentos/Tesis/src/data/radar/2015/QRO_ACUM_2015.nc")

def pruebas_multiplot():
    radar_name= "/home/arielcg/Documentos/Tesis/src/data/radar/2017/qro_radar_acum.nc"
    radar= pr.get_radar(radar_name)
    radar_subplots= list( radar.fields.keys() )

    display = pyart.graph.RadarMapDisplay(radar)
    fig = plt.figure(figsize=(15, 15))

    projection = ccrs.LambertConformal(central_latitude=radar.latitude['data'][0],
         central_longitude=radar.longitude['data'][0])

    n= 3
    plot(radar,display,fig,n,radar_subplots,projection)
    pr.plt.savefig("prueba")

def plot(radar,display,fig,n,radar_subplots,projection):
    m= len(radar_subplots)/n
    for i in range( len(radar_subplots) ):
        try:
            ax = fig.add_subplot(n,m, i, projection=projection)
            lat_0= radar.latitude['data'][0]
            lon_0= radar.longitude['data'][0]

            display.plot_ppi_map(radar_subplots[i],
                                    vmin=0,vmax=100,
                                    resolution='10m', 
                                    projection=projection,
                                    fig=fig, 
                                    ax=ax,
                                    title=radar_subplots[i],
                                    lat_0=lat_0,
                                    lon_0=lon_0,
                                    cmap=cm.get_cmap('GnBu'))
            display.plot_point(lon_0, lat_0,label_text='Radar')
        
        except:
            print(radar_subplots[i])
            continue

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

    



    
 
if __name__ == '__main__':
    #main()
    #month_acum()
    pruebas_multiplot()
    #acum_year()
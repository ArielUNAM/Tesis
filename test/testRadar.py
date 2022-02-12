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
    radar_name= "/home/arielcg/Documentos/Tesis/src/data/radar/2015/qro_radar_acum.cn"
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

 
def acum_month_2():
    for year, path in dict2data.items():
        data= pr.get_dict_of_data_path(path2root + path)
        for mes in data.keys():
            dic= {}
            acum= np.zeros((360,921))
            for dia in data[mes].keys():
                rain, radar_str= pr.get_acum_by_list( path2root + path, data[mes][dia] )
                dic['day_{}'.format(dia)]= pr.get_dic_radar_data( rain, 'Rainfall daily acum')
                acum+= rain
            
            if( data[mes].keys() ):
                dic['reflectivity']= pr.get_dic_radar_data(acum,'Rainfall month acum')
                dic['month_{}'.format(mes)]= pr.get_dic_radar_data(acum,'Rainfall month acum')
                pr.set_radar(radar_str,path2save+year+'/'+mes+'/',
                            dic,'QRO_ACUM_{}{}'.format(year,mes))
    

if __name__ == '__main__':
    #main()
    #month_acum()
    pruebas_multiplot()
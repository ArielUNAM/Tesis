import sys
sys.path.append('../')

import src.pyRadar.pyRadar as pr

import numpy as np
import matplotlib.pyplot as plt
import pyart
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

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

def print_square(name:str):
    rain= pyart.io.read(name)    
    # ploter= pr.radar_manipulator()
    # ploter.plot_geo_ppi_art("/home/arielcg/Documentos/Tesis/src/data/radar/2016/QRO_ACUM_2016.nc")
        
    la,lo,_= rain.get_gate_lat_lon_alt(0)
    minLon= 99
    maxLon= 101
    minLat= 20
    maxLat= 22

    rowsLon= []
    rowsLat= []
    for i in range(la.shape[0]):
        colsLon= []
        colsLat= []
        for j in range(la[i].shape[0]):
            if( lo[i][j] > minLon or lo[i][j] < maxLon ):
                colsLon.append( lo[i][j] )
            if( la[i][j] > minLat or la[i][j] < maxLat):
                colsLat.append( la[i][j] )
        rowsLon.append(colsLon)
        rowsLat.append(colsLat)
    
    plt.figure()
    for colLat, colLon in zip(rowsLat, rowsLon):
        for pLat, pLon in zip(colLat,colLon):
            plt.plot(pLon,pLat,'o',color='blue')

    for rowLa, rowLo in zip(la,lo):
        plt.plot(rowLo,rowLa,'o',color='red')

    plt.savefig("prueba")
   
    #radar= pyart.io.read("/home/arielcg/Documentos/Tesis/src/data/radar/2015/03/QRO_ACUM_20150329.nc")
    #manipulator= pr.radar_manipulator()

    #Para cada archivo de radar mensual
    # print(ploter.radar_bin_precipitation_estimates(rain.fields['reflectivity']['data'].data.copy(),rain.range['data'].data.copy(),rain.azimuth['data'].data.copy(),(rain.longitude['data'].copy()[0],rain.latitude['data'].copy()[0])))
    # #Se almacen el dato y las coordenadas

    
def acum_year():

    base_map= ''
    for year, path in dict2data.items():
        data= pr.get_dict_of_data_path(path2root + path)
        acum= np.zeros((360,921))
        dic= {}
        for mes in data.keys():
            #radar= pyart.io.read()
            name= path2save+year+'/'+mes+'/'+'QRO_ACUM_{}{}'.format(year,mes)+'.nc'
            try:
                radar= pyart.io.read( name  )
                data= radar.fields['month_{}'.format(mes)]['data'].data.copy()
                dic['month_{}'.format(mes)]= pr.get_dic_radar_data(data,'Rainfall month acum')
                acum+=  data
                base_map= name if not base_map else base_map
            except:
                print(path2save+year+'/'+mes+'/'+'QRO_ACUM_{}{}'.format(year,mes)+'.nc' )
        dic['reflectivity']= pr.get_dic_radar_data(acum,'Rainfall year acum')
        pr.set_radar(base_map, path2save+year+'/',
                        dic,'QRO_ACUM_{}'.format(year))

def acum_month():
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
    
    

#    radar= pr.get_radar()
    # daily_acum={}
    # for day in data['11']:

    #     daily_acum[day]=  pr.get_acum_by_path(path_to_data, data['11'][day][:3],(360,921))

    # print(daily_acum)



    # df= pd.read_csv('/home/arielcg/Documentos/Tesis/src/data/base/geoBase.csv')
    # radar= pyart.io.read_sigmet(p+l[0])
    # la,lo,_= radar.get_gate_lat_lon_alt(0)    
    # plt.plot(la,lo)
    # plt.plot(df['Latitude'],df['Longitude'],'o')
    # plt.savefig('a')
    # ploter= pr.radar_manipulator()
    # for f in l:
    #     iris= pr.get_iris_data(p+f)
    #     acum= pr.reflectivity_to_rainfall(pr.get_reflectivity(iris),pr.get_velocity(iris))
    #     print(acum.sum)
    #     ploter.plot_ppi_wrl('acum2',acum,[0,100],'/home/arielcg/Documentos/Tesis/src/data/img/'+f[10:])
    #     print(acum.sum())

        
    # ploter= pr.radar_manipulator()
    # ploter.plot_ppi_wrl('acum',acum,[0,100],'./')
    # ploter.plot_ppi_wrl('acum12',acum12,[0,100],'./')
    # ploter.plot_ppi_wrl('acum2',acum2['data'].data,[0,100],'./')
    # ploter.plot_ppi_wrl('acum21',acum21['data'],[0,100],'./')
    


def plot():
    radar= pyart.io.read_rsl(p+l[0])

    display = pyart.graph.RadarMapDisplay(radar)

    # Setting projection and ploting the second tilt
    projection = ccrs.LambertConformal(central_latitude=radar.latitude['data'][0],
                                    central_longitude=radar.longitude['data'][0])

    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(1, 1, 1)  # create an axes object in the figure
    r= radar.range['data']
    az= radar.azimuth['data']

    data= radar.fields['reflectivity']['data'].data

    # mask data array for better presentation
    mask_ind = np.where(data <= np.nanmin(data))
    data[mask_ind] = np.nan
    ma = np.ma.array(data, mask=np.isnan(data))

    cg={'radial_spacing': 14.,
    'latmin': 10e3}
    #fig = plt.figure(figsize=(12,8))
    cgax, pm = pr.wl.vis.plot_ppi(ma, r=r, az=az, fig=fig, proj='cg')
    
    display.plot_ppi_map('reflectivity', vmin=-20, vmax=20,
                    resolution='10m', projection=projection,
                    fig=fig, lat_0=radar.latitude['data'][0],
                    lon_0=radar.longitude['data'][0],min_lat=19.5, max_lat=21.69, min_lon=-101, max_lon=-99,width=31,height=10)
    display.plot_grid_lines(ax=ax)
    # Indicate the radar location with a point
    display.plot_point(radar.longitude['data'][0], radar.latitude['data'][0])
    caax = cgax.parasites[0]
    paax = cgax.parasites[1]

    t = plt.title('Decorated CG PPI', y=1.05)
    cbar = plt.gcf().colorbar(pm, pad=0.075, ax=paax)
    caax.set_xlabel('x_range [km]')
    caax.set_ylabel('y_range [km]')
    plt.text(1.0, 1.05, 'azimuth', transform=caax.transAxes, va='bottom',
            ha='right')
    cbar.set_label('reflectivity [dBZ]')
    plt.savefig('prueba3')

    cg={'angular_spacing': 20.}
    fig = plt.figure(figsize=(10,8))
    cgax, pm = pr.wl.vis.plot_ppi(ma[0:100, 0:101],
                                r=r[0:101], az=az[0:100],
                                fig=fig, proj=cg, rf=1e3,
                                infer_intervals=True,
                            )
    caax = cgax.parasites[0]
    paax = cgax.parasites[1]

    t = plt.title('Decorated Sector CG PPI', y=1.05)
    cbar = plt.gcf().colorbar(pm, pad=0.075, ax=paax)
    caax.set_xlabel('x_range [km]')
    caax.set_ylabel('y_range [km]')
    plt.text(1.0, 1.05, 'azimuth', transform=caax.transAxes, va='bottom',
            ha='right')
    cbar.set_label('reflectivity [dBZ]')

    # add floating axis
    cgax.axis["lat"] = cgax.new_floating_axis(0, 100)
    cgax.axis["lat"].set_ticklabel_direction('-')
    cgax.axis["lat"].label.set_text("range [km]")
    cgax.axis["lat"].label.set_rotation(180)
    cgax.axis["lat"].label.set_pad(10)
    plt.savefig('prueba4')

def month_plot():
    years_paths= pr.get_list_of_path_files(path2root,"QRO_201[0-9]?")
    for year_path in years_paths:
        #print(year_path[-4:])
        data= pr.get_dict_by_month(
                pr.get_dict_of_data_path( year_path ) )
        for month in data:
            acum_rain, base_radar= pr.get_acum_by_list( data[month] )
            print(acum_rain)
            print(base_radar)
        




def anual_plot():
    pass    

def season_plot():
    pass

def trim_plot():
    pass

if __name__ == '__main__':
    #main()
    month_plot()

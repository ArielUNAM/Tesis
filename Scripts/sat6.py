#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 21:14:25 2017

@author: amagaldi
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 00:18:34 2017

@author: amagaldi
"""
import glob
import os
import wradlib as wrl
import warnings
warnings.filterwarnings('ignore')
import matplotlib.pyplot as pl
import numpy as np
try:
    get_ipython().magic("matplotlib inline")
except:
    pl.ion()

from wradlib.util import get_wradlib_data_file
from wradlib.io import *
import wradlib.georef as georef
import wradlib.io as io
import wradlib.util as util

os.chdir('/Users/amagaldi/Desktop/radar/Catedral/2015')
print os.getcwd()
path =r'/Users/amagaldi/Desktop/radar/Catedral/2015/'
#CAT150922100412* CAT150922100*
allFiles = sorted(glob.glob(path + "/CAT150922100*"))
ac=np.zeros((360, 1201))
i=0
for filename in allFiles:
    f = wrl.util.get_wradlib_data_file(filename)
    fcontent = wrl.io.read_iris(f)
    nbins=(fcontent['product_hdr']['product_end']['number_bins'])
    gate_0 =(fcontent['ingest_header']['task_configuration']['task_range_info']['range_first_bin']/100)
    gate_nbin =(fcontent['ingest_header']['task_configuration']['task_range_info']['range_last_bin']/100)
    gate_size=round((gate_nbin - gate_0)/(nbins))
    range_rad=gate_0 + gate_size * np.arange(nbins, dtype='float32')
#    print range_rad[-1] , "range"
    if range_rad[-1]==298800.0 and range_rad.shape[0]==1201 :
        print filename
        print(fcontent['product_hdr']['product_configuration']['product_name'])
        print range_rad.shape, "aquí"
        range_radc_bien=range_rad
        d= fcontent['data'][1]['sweep_data']['DB_DBZ']['data']
        b = fcontent['data'][1]['sweep_data']['DB_VEL']['data']
        b[b == -3.357480314960629819] = 0   #-9999.0 no_data
        b[b != 0] = 1
        clutter = wrl.clutter.filter_gabella(d, tr1=12, n_p=6, tr2=1.1)
        data_no_clutter = wrl.ipol.interpolate_polar(d, clutter)
        pia = wrl.atten.correctAttenuationKraemer(data_no_clutter)
        data_attcorr =data_no_clutter + pia
        Z = wrl.trafo.idecibel(data_attcorr)
        R = wrl.zr.z2r(Z, a=200., b=1.6)
        depth = wrl.trafo.r2depth(R, 360)
        Zc=np.multiply(b,depth)
#        print np.amax(ac) , "max"
#        print np.sum(ac), "sum"
        ac +=Zc
        #accum = Z.sum(axis=0)
        print i, "dsffsasfd"
        i+=1
        

#ac = np.ma.masked_where(ac < 0.05, ac)
#cmap = plt.cm.OrRd
#cmap.set_bad(color='black')
fig = pl.figure(figsize=(6,5))   
im = wrl.vis.plot_ppi(ac, fig=fig)
pl.show()

#ntilt = 1
#for i in range(100):
#    try:
#        fcontent["dataset%d/what" % ntilt]
#        ntilt += 1
#    except Exception:
#        ntilt -= 1
#        break
#nrays = int(fcontent["nrays"])
#nbins = int(fcontent["nbins"])
#rscale = gate_size
#coord = np.empty((1, nrays, nbins, 3))
#
#elangle = 0.5
#coord[1,...] = georef.sweep_centroids(nrays, rscale, nbins, elangle)
## ascale = math.pi / nrays
#sitecoords = (fcontent['product_hdr']['product_end']["longitude"], fcontent['product_hdr']['product_end']["latitude"],
#              (fcontent['product_hdr']['product_end']["ground_height"]+20))

radar_location = (fcontent['product_hdr']['product_end']["longitude"], fcontent['product_hdr']['product_end']["latitude"], (fcontent['product_hdr']['product_end']["ground_height"]+20)) # (lon, lat, alt) in decimal degree and meters
elevation = 0.5 # in degree
azimuths = np.arange(0,360) # in degrees
ranges = range_radc_bien
polargrid = np.meshgrid(ranges, azimuths)
lon, lat, alt = wrl.georef.polar2lonlatalt_n(polargrid[0], polargrid[1],elevation, radar_location)
gk3 = wrl.georef.epsg_to_osr(31467)
x, y = wrl.georef.reproject(lon, lat)
xgrid = np.linspace(x.min(), x.max(), 600)
ygrid = np.linspace(y.min(), y.max(), 600)
grid_xy = np.meshgrid(xgrid, ygrid)
grid_xy = np.vstack((grid_xy[0].ravel(), grid_xy[1].ravel())).transpose()
xy=np.concatenate([x.ravel()[:,None],y.ravel()[:,None]], axis=1)
gridded = wrl.comp.togrid(xy, grid_xy, 300000., np.array([x.mean(), y.mean()]), ac.ravel(), wrl.ipol.Nearest)
gridded = np.ma.masked_invalid(gridded).reshape(600, 600)


c1, c2 = 300, 300
n = 600
r = 300

y1,x1 = np.ogrid[-c1:n-c1, -c2:n-c2]
mask = x1*x1 + y1*y1 >= r*r
gridded[mask] =-0.1 #np.nan Esto es mejor np.nan
fig = pl.figure(figsize=(10,8))
ax = pl.subplot(111, aspect="equal")
pm = pl.pcolormesh(xgrid, ygrid, gridded)
pl.colorbar(pm, shrink=0.75)
pl.xlabel("Easting (m)")
pl.ylabel("Northing (m)")

# =============================================================================
# lon2=np.tile(xgrid, (600, 1))
# ygrid= ygrid.reshape(1,600)
# lat2=np.tile(ygrid, (600, 1))
# lat2=lat2.transpose()
# 
# lat3=lat2.transpose()
# lon3=lon2.transpose()
# 
# xy1 = np.stack((lon3,lat3), axis=-1)
# =============================================================================

#data = np.stack((gridded, gridded+100, gridded+1000))
# =============================================================================
# 
# data = gridded
# ds = wrl.georef.create_raster_dataset(data, xy1)
# path =r'/Users/amagaldi/Desktop/radar/'
# wrl.io.write_raster_dataset(path + "geotiff.tif", ds, 'GTiff')
# 
# from osgeo import gdal
# ds1 = wrl.io.open_raster(path  + "geotiff.tif")
# data1, xy2, proj1 = wrl.georef.extract_raster_dataset(ds, nodata=-9999.)
# =============================================================================

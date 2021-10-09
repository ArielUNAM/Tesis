#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 23:01:38 2017

@author: amagaldi
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

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
from datetime import date, timedelta

import wradlib.georef as georef

##########################
from pyproj import CRS
from pyproj import Transformer
import pandas as pd
#########################

##################################### archivo con lat long del satelite
filename='/home/arielcg/Documentos/Tesis/src/data/base/geoBase.csv'
x=[]
y=[]
crs = CRS.from_epsg(4326)
proj = Transformer.from_crs(crs.geodetic_crs, crs)
df = pd.read_csv(filename, delimiter=",")
######################################## loop sobre el satelite lat long

for i in range (0,df.shape[0]):

        a, b= proj.transform(df.Latitude[i],df.Longitude[i])  #radar
        x.append(a)
        y.append(b)
    
x = np.array(x)
y = np.array(y)

az = np.linspace(0,360,361)[0:-1]

proj = georef.epsg_to_osr(4326)
######################

os.chdir('/home/arielcg/QRO_2015/')
print( os.getcwd())
path =r'/home/arielcg/QRO_2015/'



d1 = date(2015, 6, 1)  # start date
d2 = date(2015, 6, 8)  # end date

delta = d2 - d1         # timedelta

for i in range(delta.days + 1):
    dat=d1 + timedelta(days=i)
    ase="RAW_NA_000_236*"+'%02d'%dat.month+'%02d'%dat.day+"*"
    ase2='%02d'%dat.month+'%02d'%dat.day+".tiff"
    allFiles = sorted(glob.glob(path+ase))
    ac=np.zeros((360, 956))
    print( ase)
    print( len(allFiles))

    i=0

    for filename in allFiles:
        f = wrl.util.get_wradlib_data_file(filename)
        fcontent = wrl.io.read_iris(f)
        nbins=(fcontent['product_hdr']['product_end']['number_bins'])
        gate_0 =(fcontent['ingest_header']['task_configuration']['task_range_info']['range_first_bin']/100)
        gate_nbin =(fcontent['ingest_header']['task_configuration']['task_range_info']['range_last_bin']/100)
        gate_size=round((gate_nbin - gate_0)/(nbins))
        range_rad=gate_0 + gate_size * np.arange(nbins, dtype='float32')
        r=range_rad 
        lat=fcontent['product_hdr']['product_end']['latitude']
        lon =fcontent['product_hdr']['product_end']['longitude'] 
        lon=lon-360  ############verifica esto
        sitecoords = (lon, lat)
        #if  range_rad[-1]==239750.0 and range_rad.shape[0]==956:
        if True:
            polarneighbs = wrl.verify.PolarNeighbours(r, az, sitecoords, proj, x, y, nnear=1)
            yr=filename[41:43]
            mes=filename[43:45]
            dia=filename[44:47]
            hora=filename[47:49]
            minu=filename[49:51]
            range_radc_bien=range_rad
            print( filename)
            print((fcontent['product_hdr'])['product_configuration']['product_name'])
            d= fcontent['data'][1]['sweep_data']['DB_DBZ']['data']
            b = fcontent['data'][1]['sweep_data']['DB_VEL']['data']
            #b[b == -3.357480314960629819] = 0   #-9999.0 no_data
            b[b != 0] = 1
            clutter = wrl.clutter.filter_gabella(d, tr1=12, n_p=6, tr2=1.1)
            data_no_clutter = wrl.ipol.interpolate_polar(d, clutter)
            pia = wrl.atten.correct_attenuation_constrained(data_no_clutter)
            data_attcorr =data_no_clutter + pia
            Z = wrl.trafo.idecibel(data_attcorr)
            R = wrl.zr.z_to_r(Z, a=220., b=2.0)
            depth = wrl.trafo.r_to_depth(R, 390)
            Zc=np.multiply(b,depth)
            print(type(Zc))
            print(Zc)
            radar_at_gages = polarneighbs.extract(Zc)
            
            df2 = pd.DataFrame(radar_at_gages).T  #mejor hacer una matriz
            df2.to_csv('rad_extract.csv', index = True) #mejor hacer una matriz
            print( i, "dsffsasfd")
 

        
    print( "fin")
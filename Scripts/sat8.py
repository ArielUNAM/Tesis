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

os.chdir('/Users/amagaldi/Desktop/radar/')
print os.getcwd()
path =r'/Users/amagaldi/Desktop/radar/Catedral/2016/'



d1 = date(2016, 6, 1)  # start date
d2 = date(2016, 6, 2)  # end date

delta = d2 - d1         # timedelta

for i in range(delta.days + 1):
    dat=d1 + timedelta(days=i)
    ase="CAT16"+'%02d'%dat.month+'%02d'%dat.day+"*"
    ase2='%02d'%dat.month+'%02d'%dat.day+".tiff"
    allFiles = sorted(glob.glob(path+ase))
    ac=np.zeros((360, 1201))
    print ase
    print len(allFiles)

    i=0

    for filename in allFiles:
        f = wrl.util.get_wradlib_data_file(filename)
        fcontent = wrl.io.read_iris(f)
        nbins=(fcontent['product_hdr']['product_end']['number_bins'])
        gate_0 =(fcontent['ingest_header']['task_configuration']['task_range_info']['range_first_bin']/100)
        gate_nbin =(fcontent['ingest_header']['task_configuration']['task_range_info']['range_last_bin']/100)
        gate_size=round((gate_nbin - gate_0)/(nbins))
        range_rad=gate_0 + gate_size * np.arange(nbins, dtype='float32')
        if  range_rad[-1]==298800.0 and range_rad.shape[0]==1201:
            yr=filename[47:49]
            mes=filename[49:51]
            dia=filename[51:53]
            hora=filename[53:55]
            minu=filename[55:57]
            range_radc_bien=range_rad
            print filename
            print(fcontent['product_hdr']['product_configuration']['product_name'])
            d= fcontent['data'][1]['sweep_data']['DB_DBZ']['data']
            b = fcontent['data'][1]['sweep_data']['DB_VEL']['data']
            b[b == -3.357480314960629819] = 0   #-9999.0 no_data
            b[b != 0] = 1
            clutter = wrl.clutter.filter_gabella(d, tr1=12, n_p=6, tr2=1.1)
            data_no_clutter = wrl.ipol.interpolate_polar(d, clutter)
            pia = wrl.atten.correctAttenuationKraemer(data_no_clutter)
            data_attcorr =data_no_clutter + pia
            Z = wrl.trafo.idecibel(data_attcorr)
            R = wrl.zr.z2r(Z, a=220., b=2.0)
            depth = wrl.trafo.r2depth(R, 390)
            Zc=np.multiply(b,depth)
            print i, "dsffsasfd"
            i+=1
            ii=i
            ax, cf = wrl.vis.plot_ppi(Zc, cmap="spectral")
            pl.xlabel("Easting from radar (km)")
            pl.ylabel("Northing from radar (km)")
            pl.title("Radar Cerro Catedral"+ u'Precipitación (mm),'+yr+"-"+mes+"-"+dia+" "+hora+":"+minu)
            cb = pl.colorbar(cf, shrink=0.8)
            cb.set_label("mm")
            pl.xlim(-300,300)
            pl.ylim(-300,300)
            pl.grid(color="grey")
            #pl.show()
            ii=str(ii)
            pl.savefig(ii+'.png')

        
    print "fin"
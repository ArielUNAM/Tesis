# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 16:14:17 2018

@author: amagaldi
"""

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
from wradlib.util import get_wradlib_data_file
from wradlib.io import *
import wradlib.georef as georef
import wradlib.io as io
import wradlib.util as util
from datetime import date, timedelta

os.chdir('/home/amagaldi/Desktop/Radares/')
print os.getcwd()
path =r'/home/amagaldi/Desktop/Radares/qro/'


d1 = date(2014, 4, 11)  # start date
d2 = date(2014, 4, 13)  # end date
delta = d2 - d1         # timedelta
dat=d1
ase="RAW_NA_000_236_2015"+'%02d'%dat.month+'%02d'%dat.day+"*"
allFiles = sorted(glob.glob(path+ase))
print ase
print path
print path+ase
print len(allFiles)
ac=np.zeros((360, 921))
i=0
for filename in allFiles:
        #print filename
        f = wrl.util.get_wradlib_data_file(filename)
        fcontent = wrl.io.read_iris(f)
        nbins=(fcontent['product_hdr']['product_end']['number_bins'])
        gate_0 =(fcontent['ingest_header']['task_configuration']['task_range_info']['range_first_bin']/100)
        gate_nbin =(fcontent['ingest_header']['task_configuration']['task_range_info']['range_last_bin']/100)
        gate_size=round((gate_nbin - gate_0)/(nbins))
        range_rad=gate_0 + gate_size * np.arange(nbins, dtype='float32')
        #print range_rad[-1] , range_rad.shape[0]
        if  range_rad[-1]==236000.0 and range_rad.shape[0]==921:
         if fcontent['product_hdr']['product_configuration']['product_specific_info']['sweep_number']==1:
            yr=filename[47+5:49+5]
            mes=filename[49+5:51+5]
            dia=filename[51+5:53+5]
            hora=filename[53+5:55+5]
            minu=filename[55+5:57+5]
	    print yr, mes, dia, hora, minu	
            range_radc_bien=range_rad
            print filename
            print(fcontent['product_hdr']['product_configuration']['product_name'])
            d= fcontent['data'][1]['sweep_data']['DB_DBZ']['data']
#            b = fcontent['data'][1]['sweep_data']['DB_VEL']['data']
#            b[b == -3.357480314960629819] = 0   #-9999.0 no_data
#            b[b != 0] = 1
            clutter = wrl.clutter.filter_gabella(d, tr1=12, n_p=6, tr2=1.1)
            data_no_clutter = wrl.ipol.interpolate_polar(d, clutter)
            pia = wrl.atten.correctAttenuationKraemer(data_no_clutter)
            data_attcorr =data_no_clutter + pia
            Z = wrl.trafo.idecibel(data_attcorr)
            R = wrl.zr.z2r(Z, a=220., b=2.0)
            depth = wrl.trafo.r2depth(R, 390)
#            Zc=np.multiply(b,depth)
	    Zc=depth*4
	    ac +=Zc
            print i, "dsffsasfd"
            #ax, cf = wrl.vis.plot_ppi(Zc, cmap="spectral")
            Zc = np.ma.masked_where(Zc < 0.05, Zc)
            cmap=pl.cm.viridis
            cmap.set_bad(color='white')
            ax, cf = wrl.vis.plot_ppi(Zc, cmap="viridis")
            pl.xlabel("Easting from radar (km)")
            pl.ylabel("Northing from radar (km)")
            pl.title("Radar Queretaro"+ u'Precipitación (mm),'+yr+"-"+mes+"-"+dia+" "+hora+":"+minu)
            #cb = pl.colorbar(cf, shrink=0.8)
            cb = pl.colorbar(cf, shrink=0.8)
            cb.set_label("mm")
            pl.xlim(-300,300)
            pl.ylim(-300,300)
            pl.grid(color="grey")
            #pl.show()
            ii=i  
            ii=str(ii)
            #pl.savefig(ii+'.png')
            print path+ii+'.png'
            pl.savefig(path+ii+'.png')
            print i 
            i=i+1
ac = np.ma.masked_where(ac < 0.05, ac)
cmap=pl.cm.viridis
cmap.set_bad(color='white')
ax, cf = wrl.vis.plot_ppi(ac , cmap="viridis")
pl.xlabel("Easting from radar (km)")
pl.ylabel("Northing from radar (km)")
pl.title("Radar Queretaro"+ u'Precipitación (mm),'+yr+"-"+mes+"-"+dia+" "+hora+":"+minu)
cb = pl.colorbar(cf, shrink=0.8)
cb.set_label("mm")
pl.xlim(-300,300)
pl.ylim(-300,300)
pl.grid(color="grey")
pl.savefig(path+'acumulacion'+'.png')       
print "fin"



# -*- coding: utf-8 -*-
"""
Created on Sat Apr 21 13:53:35 2018

@author: amagaldi
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 21:56:30 2018

@author: amagaldi
"""

import matplotlib.pyplot as plt
import pyart
import os
import glob
import netCDF4
import numpy as np
from PIL import Image
import scipy.misc as misc
from datetime import date, timedelta

os.chdir('/home/amagaldi/Desktop/Radares/QRO/')
print os.getcwd()
path =r'/home/amagaldi/Desktop/Radares/QRO/'
#CAT150922100412* CAT150922100*

d1 = date(2015, 6, 11)  # start date
d2 = date(2015, 6, 30)  # end date

delta = d2 - d1         # timedelta

for i in range(delta.days + 1):
    dat=d1 + timedelta(days=i)
    ase="RAW_NA_000_236_2015"+'%02d'%dat.month+'%02d'%dat.day+"*"
    allFiles = sorted(glob.glob(path+ase))
    ac=np.zeros((360, 1201))
    print ase
    print len(allFiles)
    i=0
    for filename in allFiles:
        ase2=filename[50:64]+".png"
        ase3=filename[50:64]+".out"
        radar = pyart.io.read_sigmet(filename)
        display = pyart.graph.RadarMapDisplay(radar)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        display.plot('reflectivity', 0, vmin=-32, vmax=64.)
        plt.savefig('/home/amagaldi/Desktop/Radares/raga/'+"kk"+ase2, bbox_inches='tight')
        #plt.show()
        bris_lat    = 20.703007 
        bris_lon    = -100.447314
        fig = plt.figure(frameon=False,figsize=[4,4])
        plt.Axes(fig, [0., 0., 1., 1.])
        display.plot_ppi_map('reflectivity', 0, vmin=-14, vmax=64.,title=" ",colorbar_flag=False, cmap='pyart_Gray5', max_lat = 20.74841613631, min_lat = 20.65759786369, max_lon = -100.40190486369, min_lon = -100.49272313631)    
        display.plot_point( bris_lon, bris_lat, symbol = 'wo', markersize=1)
        plt.savefig('/home/amagaldi/Desktop/Radares/raga/'+ase2, bbox_inches='tight')
        image = misc.imread('/home/amagaldi/Desktop/Radares/raga/'+ase2)
        print image.shape
        x = np.array(image[8:229,8:214,1])
        print x.shape
        np.savetxt('/home/amagaldi/Desktop/Radares/raga/'+ase3, x,  fmt="%5.2f") 

        print "huevos"





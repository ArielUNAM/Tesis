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
os.chdir('/home/amagaldi/Desktop/Radares/QRO/')
print os.getcwd()
path =r'/home/amagaldi/Desktop/Radares/QRO/'
#CAT150922100412* CAT150922100*
allFiles = sorted(glob.glob(path + "RAW_NA_000_239_20150925045006*"))

filename = 'RAW_NA_000_239_20150925045506'

# create the plot using RadarDisplay (recommended method)
radar = pyart.io.read_sigmet(filename)
display = pyart.graph.RadarMapDisplay(radar)
#display = pyart.graph.RadarDisplay(radar)
fig = plt.figure()
ax = fig.add_subplot(111)
display.plot('reflectivity', 0, vmin=-32, vmax=64.)
plt.show()
bris_lat    = 20.703007 
bris_lon    = -100.447314
fig = plt.figure(frameon=False,figsize=[4,4])
plt.Axes(fig, [0., 0., 1., 1.])


display.plot_ppi_map('reflectivity', 0, vmin=-14, vmax=64.,title=" ",colorbar_flag=False, cmap='pyart_Gray5', max_lat = 20.74841613631, min_lat = 20.65759786369, max_lon = -100.40190486369, min_lon = -100.49272313631)
#,colorbar_flag=False
display.plot_point( bris_lon, bris_lat, symbol = 'wo', markersize=1)

plt.savefig('/home/amagaldi/Desktop/raga34.png', bbox_inches='tight')

image = misc.imread('/home/amagaldi/Desktop/raga34.png')

print image.shape

x = np.array(image[8:229,8:214,1])
print x.shape
np.savetxt('/home/amagaldi/Desktop/raga34.out', x,  fmt="%5.2f") 

<<<<<<< HEAD

=======
print "huevos"
>>>>>>> 1efd988d4a9502c2a081a8d9120471d73b4ccbcf

import matplotlib.pyplot as plt
import pyart
import os
import glob
import netCDF4
import numpy as np
from PIL import Image
import scipy.misc as misc
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
i=0
for filename in allFiles:
   print filename
   radar = pyart.io.read_sigmet(filename)
   display = pyart.graph.RadarMapDisplay(radar)
   fig = plt.figure()
   ax = fig.add_subplot(111)
   display.plot_ppi_map('reflectivity', 0, vmin=-32, vmax=64.)
   #display.plot_ppi_map('reflectivity', 0, vmin=-14, vmax=64.,title=" Radar Queretaro")
   ii=i
   ii=str(ii)
   plt.savefig(path+ii+'x.png')  
   
   i=i+1	

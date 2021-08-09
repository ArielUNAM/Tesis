from os import path
import sys
#sys.path.insert(1,'/src/botddigger')
sys.path.append('../')

import src.pyRadar.pyRadar as pr

path2root= "/home/arielcg/"
#path2data= {'2015':'QRO_2015/','2016':'QRO_2016/','2017':'QRO_2017/'}
path2data= {'2015':'QRO_2015/'}
path2save= "/home/arielcg/Documentos/Tesis/src/data/radar/"

for year, ypath in path2data.items():
    path= path2root+ypath
    pr.saveday(path,path2save,year)
import os
import sys

from tqdm.std import TRLock
#sys.path.insert(1,'/src/botddigger')
sys.path.append('../')

import src.pyRadar.pyRadar as pr

path2root= "/home/arielcg/"
path2data= {'2015':'QRO_2015/','2016':'QRO_2016/','2017':'QRO_2017/'}
#path2data= {'2015':'QRO_2015/'}
path2save= "/home/arielcg/Documentos/Tesis/src/data/radar/"


# for year, ypath in path2data.items():
#     path= path2root+ypath
#     names= os.listdir(path)
#     print(lenthg(names[0]))

data= pr.getDataByDay('2015','05','02',path2root+'QRO_2015/',pr.ELEVATION,pr.SCANN_RANGE,pr.PARAM_VEL,pr.PARAM_TRANS,'RAW_NA_000_236_')

print(data)
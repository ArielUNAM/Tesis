import sys
#sys.path.insert(1,'/src/botddigger')
sys.path.append('../')

import src.pyRadar.pyRadar as pr

path= '/home/arielcg/Documentos/Tesis/src/data/radar/'
img= '/home/arielcg/Documentos/Tesis/src/data/img/'
sdt= 'week'

files= pr.path2file(sdt,path)
pr.plot_data(sdt,files,img+sdt+'/')


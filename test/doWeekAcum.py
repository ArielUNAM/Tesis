import sys
#sys.path.insert(1,'/src/botddigger')
sys.path.append('../')

import src.pyRadar.pyRadar as pr


path= '/home/arielcg/Documentos/Tesis/src/data/radar/'

pr.saveweek(path)

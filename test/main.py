import sys
sys.path.append('../')

import src.pyRadar.pyRadar as pr
from numpy import load



path2root= "/home/arielcg/"
path2save= "/home/arielcg/Documentos/Tesis/src/data/radar/"
path2fig= '/home/arielcg/Documentos/Tesis/src/data/img/'

dict2data= {'2015':'QRO_2015/','2016':'QRO_2016/','2017':'QRO_2017/'}

#dict2data= {'2017':'QRO_2017/'}

d= ['/home/arielcg/Documentos/Tesis/src/data/radar/2015/04/radar_2015_04_13.npz','/home/arielcg/Documentos/Tesis/src/data/radar/2015/04/radar_2015_04_15.npz','/home/arielcg/Documentos/Tesis/src/data/radar/2015/04/radar_2015_04_16.npz','/home/arielcg/Documentos/Tesis/src/data/radar/2015/04/radar_2015_04_17.npz','/home/arielcg/Documentos/Tesis/src/data/radar/2015/04/radar_2015_04_18.npz']

def main():        
    pass


if __name__ == '__main__':
    main()

import sys

from numpy import load

#sys.path.insert(1,'/src/botddigger')
sys.path.append('../')

import src.pyRadar.pyRadar as pr

path2root= "/home/arielcg/"
#dict2data= {'2015':'QRO_2015/','2016':'QRO_2016/','2017':'QRO_2017/'}
dict2data= {'2017':'QRO_2017/'}
path2save= "/home/arielcg/Documentos/Tesis/src/data/radar/"
path2fig= '/home/arielcg/Documentos/Tesis/src/data/img/'

pr.acum_month(path2save,'2015')

d= ['/home/arielcg/Documentos/Tesis/src/data/radar/2015/04/radar_2015_04_13.npz','/home/arielcg/Documentos/Tesis/src/data/radar/2015/04/radar_2015_04_15.npz','/home/arielcg/Documentos/Tesis/src/data/radar/2015/04/radar_2015_04_16.npz','/home/arielcg/Documentos/Tesis/src/data/radar/2015/04/radar_2015_04_17.npz','/home/arielcg/Documentos/Tesis/src/data/radar/2015/04/radar_2015_04_18.npz']

def main():
    pr.acum_daily(path2root,path2save,dict2data)
    for year,_ in dict2data.items():
        pr.acum_week(path2save,year)

    # name=0
    # ploter= pr.create_radar_visualizator()
    # for dt in d:
    #     name+=1
    #     ploter.ppi_art(str(name),load(dt),[0,200],path2fig)
    

        
if __name__ == '__main__':
    main()

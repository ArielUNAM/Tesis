import sys

from numpy import load

#sys.path.insert(1,'/src/botddigger')
sys.path.append('../')

import src.pyRadar.pyRadar as pr

path2root= "/home/arielcg/"
#path2data= {'2015':'QRO_2015/','2016':'QRO_2016/','2017':'QRO_2017/'}
dict2data= {'2015':'QRO_2015/'}
path2save= "/home/arielcg/Documentos/Tesis/src/data/radar/"
path2fig= '/home/arielcg/Documentos/Tesis/src/data/img/'

l= ['/home/arielcg/Documentos/Tesis/src/data/radar/2015/03/radar_2015_03_10.npz','/home/arielcg/Documentos/Tesis/src/data/radar/2015/03/radar_2015_03_11.npz','/home/arielcg/Documentos/Tesis/src/data/radar/2015/03/radar_2015_03_12.npz','/home/arielcg/Documentos/Tesis/src/data/radar/2015/03/radar_2015_03_13.npz']
def main():
    #pr.acum_daily(path2root,path2save,dict2data)
    #pr.acum_week(path2save,'2015','03')
    name=0
    ploter= pr.create_radar_visualizator()
    for dt in l:
        name+=1
        ploter.ppi_art(str(name),load(dt),[0,200],path2fig)
    

        
if __name__ == '__main__':
    main()

from os import path
import sys
#sys.path.insert(1,'/src/botddigger')
sys.path.append('../')

import src.pyRadar.pyRadar as pr
from tqdm import tqdm

path2root= "/home/arielcg/"
#path2data= {'2015':'QRO_2015/','2016':'QRO_2016/','2017':'QRO_2017/'}
path2data= {'2015':'QRO_2015/'}
path2save= "/home/arielcg/Documentos/Tesis/src/data/radar/"

months= ['01','02','03','04','05']
def main():
    for year, path in path2data.items():
        dic_of_data= pr.get_dict_of_data_path(path2root+path)
        pr.generate_directory_structure(dic_of_data,year,path2save)
        #for month in dic_of_data.keys():
        for month in tqdm(months):
            days= dic_of_data[month].keys()
            if ( days ):
                for day in days:
                    pr.generate_daily_acum(path2root+path,dic_of_data,path2save,year,month,day)
        
if __name__ == '__main__':
    main()
import src.pyRadar.pyRadar as pr

path2root= "/home/arielcg/"
path2data= {'2015':'QRO_2015','2016':'QRO_2016','2017':'QRO_2017'}

path2save= "/home/arielcg/Documentos/Tesis/src/data/"

for year, ypath in path2data.items():
    pr.saveday(path2root,ypath,path2save,year)
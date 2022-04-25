import wradlabfnc as wl
import numpy as np
import matplotlib.pyplot as pl

#############################
#############
#Obtenemos el directorio donde se almacenan los datos y
# obtenemos una lista ordendad de todos los datos que cumplan
# con estar en el directorio y pertenecer al intervalo de 
# fechas dado en la función list_data
#path = "/home/aceron/Documentos/GitHub/Tesis/datos/OneDrive_3_1-3-2021/"
path = "datos/OneDrive_1_1-8-2021/"
ldatos = wl.list_data(path,2015,1,1,2015,1,4)
##########
#Leemos cada archivo y lo separamos por día para obtener
# un acumulativo diario
day = ldatos[0][7:9]
contador = 0
Maccum = np.zeros((360,1201))


#for data in ldatos[:20]:
for data in ldatos:
    if data[7:9] == day:
        #Lee los datos, transforma y suma el resultado
        #fcontent = wl.read_data(path,data,elev=1,dist=298800,shape=1201)
        fcontent = wl.read_data(path,data,elev=1)
        #print(type(fcontent))
        if type(fcontent) is tuple:
            wl.writeLog(data[0]+":"+data[1])
        else:
            print("Datos del día: ",day)
            #Comprueba la elevación, buscamos la más baja
            contador += 1
            #print(fcontent)
            dBZ = fcontent['data'][1]['sweep_data']['DB_DBZ']['data']
            vel = fcontent['data'][1]['sweep_data']['DB_VEL']['data']
            ###
            vel[vel == -3.357480314960629819] = 0
            vel[vel != 0] = 1
            ###
            dBZ_cor = wl.preProcess(dBZ)
            Zc = wl.dBZ_to_Zc(dBZ_cor,vel)
            print("Z mean: ",Zc.mean())
            Maccum = np.add(Maccum,Zc)
        
    else:
        #Plot
        #fig = pl.figure(figsize=(10,8))
        #wl.plot_ppi(fig,Maccum,title="No",xlabel="Easting from radar (km)",ylabel="Northing from radar (km)",cmap="viridis")
        #pl.show()
        print("Acumulado dek dia: ",day)
        print("Z mean: ",Maccum.mean())
        print(Maccum)
        Maccum = np.zeros((360,1201))
        contador = 0
        #Lee los datos, transforma y suma el resultado
        fcontent = wl.read_data(path,data)
        if fcontent is tuple:
            writeLog(data[0]+":"+data[1])
        else:
            contador += 1
            dBZ = fcontent['data'][1]['sweep_data']['DB_DBZ']['data']
            vel = fcontent['data'][1]['sweep_data']['DB_VEL']['data']
            dBZ_cor = wl.preProcess(dBZ)
            Zc = wl.dBZ_to_Zc(dBZ_cor,vel)
            Maccum = wl.add_matrix(Maccum,Zc,contador)
    day = data[7:9]
#print(Maccum.shape)
print(Maccum)
#Plot
#fig = pl.figure(figsize=(10,8))
#wl.plot_ppi(fig,Maccum,title="No",xlabel="Easting from radar (km)",ylabel="Northing from radar (km)",cmap="viridis")
#pl.show()

                

#Se puede generar un nuevo ciclo para generar los datos mensuales
#Se puede generar un nuevo ciclo para generar los datos anuales
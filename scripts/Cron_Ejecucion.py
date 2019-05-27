import matplotlib
matplotlib.use('Agg')
#matplotlib.use ('template')
import matplotlib.pyplot as plt
import datetime
import numpy as np
import pandas as pd
import pylab as pl
import sys, getopt
import time
import os
import netCDF4
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import cPickle
from wmf import wmf

ff = datetime.datetime.now()

mes = ff.month ; dia = ff.day ; hora = ff.hour ; minuto = ff.minute
if mes < 10:
	mes = '0'+str(ff.month)
mes = str(mes)
if dia < 10:
	dia = '0'+str(ff.day)
dia = str(dia)
if hora < 10:
        hora = '0'+str(ff.hour)
hora = str(hora)
if minuto < 10:
        minuto = '0'+str(ff.minute)
minuto = str(minuto)
date1 = str(ff.year)+'-'+mes+'-'+dia+'-'+hora+':'+minuto

print 'Fecha-hora del mapa a generar'
print date1

path='/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/'

#Ejecutar mapa de precipitacion
print '                                           '
print '--------- Mapa de lluvia ------------------'
print '                                           '

comando = 'python '+path+'Rain_operacional.py'
os.system(comando)

print '                                     '
print '1. El mapa de lluvia ha sido generado'


#Ejecutar mapa de humedad
print '                                          '
print '--------- Mapa de humedad ----------------'
print '                                          '

comando = 'python '+path+'Hum_operacional.py'
os.system(comando)

print '                                     '
print '2. El mapa de humedad ha sido generado'


#Ejecutar mapa de temperatura
print '                                          '      
print '--------- Mapa de temperatura ------------'
print '                                          '

comando = 'python '+path+'Temp_operacional.py'
os.system(comando)

print '                                     '
print '3. El mapa de temperatura ha sido generado'

#Ejecutar temperatura maxima
print  '                                        '
print  '-----------Factor temperatura-----------'
print  '                                        '

comando = 'python '+path+'Factor_Temp.py'
os.system(comando) 

#Ejecutar mapa de susceptibilidad de incendios
print '                                            '
print '--------------------------------------------'
print '----- Mapa de susceptibilidad --------------'
print '--------------------------------------------'
print '                                            '

cu = wmf.SimuBasin(rute='/media/nicolas/Home/nicolas/01_SIATA/nc_cuencas/Cuenca_AMVA_Barbosa_Incendios.nc',) #Cargar la cuenca

#Carga mapa de costos 
g = netCDF4.Dataset('/media/nicolas/Home/nicolas/01_SIATA/nc_cuencas/Cuenca_AMVA_Barbosa_Incendios.nc')
ME = g.variables['RiesgosIncendios'][:]
g.close()

#Carga mapa de historicos
f=open('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/series/suma_binario.bin','r')
MH=cPickle.load(f)
f.close()

#Carga mapa de de lluvia operacional
f=open('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/mapa_rain_operacional.bin','r')
mapa_rain=cPickle.load(f)
f.close()

#Carga mapa de de humedad operacional
f=open('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/mapa_humedad_operacional.bin','r')
mapa_hum=cPickle.load(f)
f.close()

#Carga mapa de de temperatura operacional
f=open('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/mapa_temperatura_operacional.bin','r')
mapa_temp=cPickle.load(f)
f.close()

#Calcular mapa de susceptibilidad de incendios operacional

umb_temp = 22 #Umbral para declarar vulnerabilidad nula de incendios forestales
Wr=0.41 ; Wh=0.39 ; We=0.10 ; Whis=0.08 #Pesos para cada variable hallado desde la calibracion

susc = (mapa_rain*Wr) + (mapa_hum*Wh) + (ME*We) + (MH*Whis)
susc[np.where(np.array(mapa_temp) < umb_temp)[0]] = 0.01
susc[np.where(np.array(ME) == 0)[0]] = 0

import matplotlib.colors as mcolors
def make_colormap(seq):
    seq = [(None,) * 3, 0.0] + list(seq) + [1.0, (None,) * 3]
    cdict = {'red': [], 'green': [], 'blue': []}
    for i, item in enumerate(seq):
        if isinstance(item, float):
            r1, g1, b1 = seq[i - 1]
            r2, g2, b2 = seq[i + 1]
            cdict['red'].append([item, r1, r2])
            cdict['green'].append([item, g1, g2])
            cdict['blue'].append([item, b1, b2])
    return mcolors.LinearSegmentedColormap('CustomMap', cdict)

r1=98/255. ; g1=210/255. ; b1=221/255. ; r2=63/255. ; g2=125/255. ; b2=170/255.
r3=237/255. ; g3=226/255. ; b3=20/255. ; r4=214/255. ; g4=30/255. ; b4=30/255.
rvb = make_colormap([(r1,g1,b1), 0.25, (r2,g2,b2), 0.50, (r3,g3,b3), 0.75, (r4,g4,b4)])

a = np.copy(susc)
a[a==0]=np.nan
a[len(a)-1] = 0.8

cu.Plot_basinClean(a, lines_spaces=0.1, cmap=pl.get_cmap(rvb,4),show_cbar=False,cbar_ticks=[0.12,0.32,0.52,0.72],cbar_ticklabels=['Nula','Baja','Media','Alta'],figsize=(15,20),ruta='/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/mapa_suscep.png')
os.system('cp /media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/mapa_suscep.png /media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/Fig_historia/mapa_inc_'+date1+'.png')

print '                                           '
print '4. El mapa de susceptibildad ha sido generado'

f=open('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/mapa_suscep_operacional.bin','w')
cPickle.dump(susc,f)
f.close()

#Guardar archivo historico
ff = datetime.datetime.now()

try:
    rut='/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/historial' 
    cu.rain_radar2basin_from_array(vec=susc,ruta_out=rut,fecha=ff,doit=True,status='old')
    cu.rain_radar2basin_from_array(vec=susc,ruta_out=rut,fecha=ff,doit=True)
    cu.rain_radar2basin_from_array(vec=susc,ruta_out=rut,fecha=ff,doit=True,status='close')
except:
    str_susc = ''.join(','+str(e) for e in susc)
    with open('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/historial.txt','a') as f:
        f.write(str(ff.year)+'-'+str(ff.month)+'-'+str(ff.day)+'-'+str(ff.hour)+':'+str(ff.minute)+str_susc+' \n')

    

print '                             '
print '-----------------------------'
print '5. Archivo guardado en historico'

#Guardar archivos tif agregado y distribuido

#Mapa distribuido
cu.Transform_Basin2Map(susc,ruta='/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/mapa_susc_dist.tif')

#Mapa agregado
path_tif='/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/scripts/ZonasPronostico.tif'
mapa_zonas,prop=wmf.read_map_raster(path_tif) #Leer mapa de regiones
zonas_basin = cu.Transform_Map2Basin(mapa_zonas, prop) #Escribir el mapa en forma de cuenca
zonas_basin[zonas_basin < 0] = 0

mapa_suscep_agre = np.zeros(cu.ncells)

###nuevo
for i in np.arange(1,13,1):
    pp = np.where(np.array(zonas_basin) == i)[0]
    hist=np.histogram(susc[pp],[0,0.22,0.42,0.62,0.87])
    posmoda=np.where(hist[0]==max(hist[0]))[0]
    moda=[0.14,0.34,0.54,0.73][posmoda[0]]#hist[1][posmoda]
    mapa_suscep_agre[pp]=moda
    

#original
#for i in np.arange(1,13,1):
#    pp = np.where(np.array(zonas_basin) == i)[0]
#    mapa_suscep_agre[pp] = np.percentile(susc[pp],50)

gh=open('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/mapasusc.bin','w')
cPickle.dump(mapa_suscep_agre,gh)
gh.close()
    
a = np.copy(mapa_suscep_agre)
a[np.where((a == 0) & (zonas_basin != 5))[0]]=np.nan #nan en zonas por fuera de la jurisdiccion del VA y 0 en zona centro de Medellin
cu.Transform_Basin2Map(a,ruta='/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/mapa_susc_agre.tif')

print '                                           '
print '6. Mapas agregado y distribuido guardados'

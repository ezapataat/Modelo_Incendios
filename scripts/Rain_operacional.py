#Este programa es la version en python de /media/Home/nicolas/Jupyter/Esneider/incendios_forestales/RNA_entradas/scripts/Lectura_LluviaRadar.ipynb

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
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import cPickle
from wmf import wmf
import glob
import netCDF4

cu = wmf.SimuBasin(rute='/media/nicolas/Home/nicolas/01_SIATA/nc_cuencas/Cuenca_AMVA_Barbosa_C.nc') #Lectura de la cuenca

#Generar mapa de acumulado y de sequia de 15 dias
def ReadAcum_radar(ruta,fi,ff,umb=6):
    vec_acum = np.zeros(cu.ncells)
    dias_sequia=np.ones(cu.ncells) ; dias_sequia[0::] = 15

    for i in ruta:
        date_file = datetime.datetime(int(i.split('/')[6][0:4]), int(i.split('/')[6][4:6]), int(i.split('/')[6][6:8]),
                                        int(i.split('/')[6][8:10]), int(i.split('/')[6][10:12]))
        if (date_file >= fi) and (date_file <= ff):
            g = netCDF4.Dataset(i)
            RadProp = [g.ncols, g.nrows, g.xll, g.yll, g.dx, g.dx]                        
            rvec = cu.Transform_Map2Basin(g.variables['Rain'][:].T / (12*1000), RadProp)
            g.close()
            vec_acum += rvec
        
        pos = np.where((np.array(vec_acum) >= umb) & (np.array(dias_sequia) == 15))[0]
        if len(pos) > 1:
            tt = ff-date_file
            try:
                dias_sequia[pos]=int(str(tt).split(' ')[0])
            except:
                dias_sequia[pos]=0
            
    return vec_acum, dias_sequia


FH2 = datetime.datetime.now() +  datetime.timedelta(hours=5) #Fecha actual en UTC
FH1 = FH2 - datetime.timedelta(days=20) #Fecha actual en UTC - 15 dias
mm1 = FH1.month ; mm2 = FH2.month

print 'Rango de fechas para lluvia radar'
print FH1
print FH2

if mm1 < 10:
    mm1 = '0'+str(mm1)
mm1 = str(mm1)
if mm2 < 10:
    mm2 = '0'+str(mm2)
mm2 = str(mm2)

yy1 = str(FH1.year)+str(mm1)
yy2 = str(FH2.year)+str(mm2)

if yy1 != yy2: #El periodo abarca meses diferentes
    #print 'Distinto mes'
    listado1 = glob.glob('/media/nicolas/Home/nicolas/101_RadarClass/'+yy1+'*')
    listado2 = glob.glob('/media/nicolas/Home/nicolas/101_RadarClass/'+yy2+'*')
    listado1.extend(listado2)
    ff = [datetime.datetime(int(i.split('/')[6][0:4]), int(i.split('/')[6][4:6]), int(i.split('/')[6][6:8]),
                            int(i.split('/')[6][8:10]), int(i.split('/')[6][10:12])) for i in listado1]
    cc = sorted(range(len(ff)), key=lambda k: ff[k],reverse=True) #fechas de atras hacia adelante
    z = ReadAcum_radar(np.array(listado1)[cc],FH1,FH2)
    
if yy1 == yy2: #El periodo esta en el mismo mes
    #print 'Igual mes'
    listado = glob.glob('/media/nicolas/Home/nicolas/101_RadarClass/'+yy1+'*')
    ff = [datetime.datetime(int(i.split('/')[6][0:4]), int(i.split('/')[6][4:6]), int(i.split('/')[6][6:8]), 
        int(i.split('/')[6][8:10]), int(i.split('/')[6][10:12])) for i in listado]
    cc = sorted(range(len(ff)), key=lambda k: ff[k],reverse=True) #fechas de atras hacia adelante
    z = ReadAcum_radar(np.array(listado)[cc],FH1,FH2)
    
#Clasificar por puntajes segun acumulados para 15 dias
Vsum_cla = np.zeros(cu.ncells)

#hist_incen15 = np.array([746., 129., 85., 63., 42., 40., 36., 27., 17., 14.])
#ejex_acum = [0., 4.66, 9.32, 13.98, 18.65, 23.31, 27.97, 32.64, 37.30, 41.96, 10000. ]
#hist_incen15 = np.array([611., 82., 49., 45., 33., 19., 13., 11., 5., 4.]) #Reglas nuevas

ejex_acum = np.array([0., 4.98, 9.97, 14.95, 19.94, 24.92, 29.91, 34.90, 39.88, 44.87, 10000.])
hist_incen15 = np.array([1658., 378., 261., 192., 134., 96., 64., 61., 50., 38.]) #Reglas para 2o dias

for cla in range(1,len(ejex_acum),1):
        inf = ejex_acum[cla-1] ; sup = ejex_acum[cla] ; valor = hist_incen15[cla-1]/sum(hist_incen15)
        Vsum_cla[np.where((np.array(z[0]) >= inf) & (np.array(z[0]) < sup))[0]] = valor

#Clasificar por puntajes
dias_seq_cla = np.zeros((cu.ncells))

#ejex_sequia = np.array([0, 1.3, 4.66, 8 , 11.33, 14.66, 20])
ejex_sequia = np.array([0., 1.87, 3.75, 5.62, 7.5, 9.37, 11.25, 13.12, 20])
hist_sequia = np.array([34., 80., 79., 78., 76., 92., 145., 310.]) #Nuevas reglas
for cla in range(1,len(ejex_sequia),1):
        inf = ejex_sequia[cla-1] ; sup = ejex_sequia[cla] ; valor = hist_sequia[cla-1]/sum(hist_sequia)
        dias_seq_cla[np.where((np.array(z[1]) >= inf) & (np.array(z[1]) < sup))[0]] = valor

mapa_rain = Vsum_cla + dias_seq_cla

a = np.copy(mapa_rain)
coordsX = wmf.cu.basin_coordxy(cu.structure,cu.ncells)[0] #longitudes del mapa
coordsY = wmf.cu.basin_coordxy(cu.structure,cu.ncells)[1] #latitudes del mapa
b = np.where((np.array(coordsY) < 6.06) & (np.array(coordsX) > -75.61))[0]
c = np.where((np.array(coordsY) < 6.06) & (np.array(coordsX) < -75.61))[0]
a[b] = np.percentile(mapa_rain[c],50)


f=open('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/mapa_rain_operacional.bin','w')
cPickle.dump(a,f)
f.close()


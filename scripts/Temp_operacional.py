#Este programa es la version en python de /media/Home/nicolas/Jupyter/Esneider/incendios_forestales/RNA_entradas/scripts/Lectura_temperatura.ipynb

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

enlace_madera='/media/result_WRF/' #Ruta de los mapas de temperatura en Madera 
path='/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/'
cu = wmf.SimuBasin(rute='/media/nicolas/Home/nicolas/01_SIATA/nc_cuencas/Cuenca_AMVA_Barbosa_C.nc') #Leer la cuenca

#Leer mapas relacionados con temperatura pronosticada (datos, latitud, longitud)
date = datetime.datetime.now()+datetime.timedelta(hours=5) #Hora en UTC
mm = date.month ; dd = date.day ; hh = date.hour
if mm < 10:
    mm = '0'+str(mm)
mm = str(mm)
if dd < 10:
    dd = '0'+str(dd)
dd = str(dd)
if hh < 10:
    hh = '0'+str(hh)
hh = str(hh)

archivo = str(date.year)+'-'+mm+'-'+dd+'_'+hh
archivo1 = str(date.year)+'-'+mm+'-'+dd
print 'Fecha del archivo de temperatura'
print archivo
data_temp = np.genfromtxt(enlace_madera+'T2_'+archivo+'_05', delimiter=' ')
data_temp = data_temp - 272.15
lat_temp = np.genfromtxt(enlace_madera+'lat.txt', delimiter=' ')
lon_temp = np.genfromtxt(enlace_madera+'lon.txt', delimiter=' ')

#Mapa de temperatura ambiente maxima para el dia en curso

ncols = 135 ; nrows = 135
yll = np.min(lat_temp) ; xll = np.min(lon_temp)
size1 = lat_temp[1][0] - lat_temp[0][0] ; size2 = lon_temp[1][1] - lon_temp[1][0]
no_data = -9999
prop = [ncols, nrows, xll, yll, size1, size2, no_data]
temp_basin = cu.Transform_Map2Basin(data_temp[::-1].T, prop) #Escribir el mapa en forma de cuenca

#Interpolar temperatura ambiente a resolucion del modelo 
cu.GetGeo_Cell_Basics()
alturas = cu.CellHeight
elevacion = np.zeros((135,135))
x = [] ; y = []

for i in range(135):
    for j in range(135):
        xy = [lon_temp[i,j], lat_temp[i,j]]
        elev = wmf.cu.basin_extract_var_by_point(cu.structure,alturas,xy,3,1,cu.ncells)
        elevacion[i,j] = elev
        x.append(elev[0]) ; y.append(data_temp[i,j])

elev_basin = cu.Transform_Map2Basin(elevacion[::-1].T, prop)

pos = np.where(np.array(x) > 1000)[0]
x = np.array(x)[pos] ; y = np.array(y)[pos]
z = np.polyfit(x, y, 1)
tmp = x*z[0] + z[1]
temp_basin1 = alturas*z[0]+z[1]

#Reglas para temperatura superficial, las cuales fueron halladas con imagen satelital de 2015-12-29
f=open(path+'/series/reglaTsup.bin','r')
reglas_Tsup=cPickle.load(f)
f.close()

f=open(path+'/series/reglaTsup_ejes.bin','r')
ejes_Tsup=cPickle.load(f)
f.close()

#Temperatura superficial
ejex_temp = (ejes_Tsup[0:-1]+ejes_Tsup[1::])/2
temp_sup = np.zeros(cu.ncells)

for i in range(len(temp_basin1)):
    ta = temp_basin1[i]
    for j in range(len(ejex_temp)-1):
        regla = reglas_Tsup['P75']
        if (ta >= np.array(ejex_temp)[j]) and (ta <= np.array(ejex_temp)[j+1]):
            z1 = np.polyfit([np.array(ejex_temp)[j],np.array(ejex_temp)[j+1]], [regla[j],regla[j+1]], 1)
            tmp = ta*z1[0] + z1[1]
            temp_sup[i] = tmp

        if ta >= np.array(ejex_temp[len(ejex_temp)-1]):
            z1 = np.polyfit([np.array(ejex_temp)[len(ejex_temp)-2],np.array(ejex_temp)[len(ejex_temp)-1]], [regla[len(regla)-2],regla[len(regla)-1]], 1)
            tmp = ta*z1[0] + z1[1]
            temp_sup[i] = tmp

        if ta <= np.array(ejex_temp[0]):
            z1 = np.polyfit([np.array(ejex_temp)[0],np.array(ejex_temp)[1]], [regla[0],regla[1]], 1)
            tmp = ta*z1[0] + z1[1]
            temp_sup[i] = tmp
            
f=open('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/mapa_temperatura_operacional.bin','w')
cPickle.dump(temp_sup,f)
f.close()


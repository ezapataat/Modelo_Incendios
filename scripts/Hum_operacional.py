#Este programa es la version en python de /media/Home/nicolas/Jupyter/Esneider/incendios_forestales/RNA_entradas/scripts/Lectura_humedad_ope.ipynb

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

#path_amazonas='/media/StorageBarbosa/' #Ruta de los mapas de storage operacionales 
path_amazonas='/media/nicolas/Home/Jupyter/Soraya/Op_Alarmas/Op_AMVA60m/03_Resultados/03_almacenamiento/' #Ruta de los mapas de storage operacionales
cu = wmf.SimuBasin(rute='/media/nicolas/Home/nicolas/01_SIATA/nc_cuencas/Cuenca_AMVA_Barbosa_C.nc') #Lectura de la cuenca

#Leer almacenamiento capilar operacional
arch = 'CuBarbosa_001_001.StO' 
hdr = np.loadtxt(path_amazonas+arch+'hdr',skiprows=5,dtype=str)
fecha = hdr[0][6]
print 'Fecha ultimo almacenamiento'
print fecha
v,p = wmf.models.read_float_basin_ncol(path_amazonas+arch+'bin',1,cu.ncells, 5)

#Asignar puntajes
mapa_hum = v[0]
hum_cla = np.zeros((cu.ncells))
ejex_hum = np.array([0., 0.98, 1.96, 2.94, 3.92, 4.90, 5.88, 6.86, 7.85, 8.83, 9.81])
hist_hum = np.array([950., 21., 15., 14., 4., 6., 7., 6., 6., 4.])
for cla in range(1,len(ejex_hum),1):
        inf = ejex_hum[cla-1] ; sup = ejex_hum[cla] ; valor = hist_hum[cla-1]/sum(hist_hum)
        hum_cla[np.where((np.array(mapa_hum) >= inf) & (np.array(mapa_hum) < sup))[0]] = valor

f=open('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/mapa_humedad_operacional.bin','w')
cPickle.dump(hum_cla,f)
f.close()

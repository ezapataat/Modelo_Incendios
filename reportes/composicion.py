import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import pylab as pl
from matplotlib.dates import DateFormatter
from wmf import wmf
import pandas as pd
import cPickle
from osgeo import gdal, osr  
from osgeo.gdalconst import *
from netCDF4 import Dataset
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.patches import PathPatch
import os, sys, time  


date = dt.datetime.now()
date1 = date - dt.timedelta(days=6)

mm = date.month ; dd = date.day ; hho = date.hour
if mm < 10:
    mm = '0'+str(mm)
if dd < 10:
    dd = '0'+str(dd)
if hho < 10:
    hho = '0'+str(hho)
   
mm1 = date1.month ; dd1 = date1.day
if mm1 < 10:
    mm1 = '0'+str(mm1)
if dd1 < 10:
    dd1 = '0'+str(dd1)
  
date_str = str(dd1)+'/'+str(mm1)+'/'+str(date1.year)+' - '+str(dd)+'/'+str(mm)+'/'+str(date.year)
date1_str = str(date.year)+'/'+str(mm)+'/'+str(dd)+' '+str(hho)+':00'
hora_str = str(hho)+':00'

plt.close('all')
fig = plt.figure(figsize=(3.535,4.535),facecolor='w',edgecolor='w')
plt.subplots_adjust(wspace=.3,hspace=.5,bottom=0.05,left=0.05,right=0.95,top=0.95)

ax={}
i=0
ax[i]= fig.add_subplot(111)
plt.setp(ax[i].spines.values(), color=(0.7, 0.7, 0.7))
ax[i].tick_params(axis=u'both', which=u'both',length=0, colors=(0.45, 0.45, 0.45))

ax[0].set_xlim(0,1)
ax[0].set_xticklabels('')
ax[0].set_yticklabels('')

ax[0].axhline(y=.96, xmin=0.05, xmax=0.95,color=(0.94, 0.94, 0.94),lw=15)
ax[0].text(0.01,0.955,u'               Comportamiento ultimas 6 horas',ha='left',va='center',fontsize='small',color=(0.24, 0.24, 0.24))

plt.savefig('marco.pdf',bbox_inches='tight')

os.system("convert -background transparent -fill white -gravity center -size 240x90 label:"+"'"+date_str+"'"+" /media/nicolas/Home/Jupyter/Esneider/incendios_forestales/reportes/fecha.png")
os.system("convert -background transparent -fill 'rgb(10,32,46)' -gravity center -size 185x54 label:"+"'"+date1_str+"'"+" /media/nicolas/Home/Jupyter/Esneider/incendios_forestales/reportes/fecha1.png")

# Reporte con mapa distribuido
path = '/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/reportes/'
os.system('convert -resize 52.% '+path+'Mapa_D.png '+path+'Mapa_D_1.png')
os.system('convert -resize 34.15% '+path+'reporte_6horas.png '+path+'reporte_6horas_1.png')
os.system('convert -density 500 -quality 100 -resize 29.6% '+path+'marco.pdf '+path+'marco_1.png')
os.system('composite -geometry +10+240 '+path+'Mapa_D_1.png '+path+'PlantillaReporte1.png '+path+'Reporte_incendios1.png')
os.system('composite -geometry +630+243.7 '+path+'marco_1.png '+path+'Reporte_incendios1.png '+path+'Reporte_incendios1.png')
os.system('composite -geometry +308+170 '+path+'fecha1.png '+path+'Reporte_incendios1.png '+path+'Reporte_incendios1.png')
os.system('composite -geometry +667+303.3 '+path+'reporte_6horas_1.png '+path+'Reporte_incendios1.png '+path+'Reporte_incendios1.png')

# Reporte con mapa agregado
os.system('convert -density 500 -quality 100 -resize 10.5% '+path+'Mapa_A.pdf '+path+'Mapa_A_1.png')
os.system('convert -density 500 -quality 100 -resize 30.% '+path+'reporte_semanal.pdf '+path+'reporte_semanal_1.png')
os.system('composite -geometry +10+250 '+path+'Mapa_A_1.png '+path+'PlantillaReporte2.png '+path+'Reporte_incendios2.png')
os.system('composite -geometry +308+170 '+path+'fecha1.png '+path+'Reporte_incendios2.png '+path+'Reporte_incendios2.png')
os.system('composite -geometry +610+250 '+path+'reporte_semanal_1.png '+path+'Reporte_incendios2.png '+path+'Reporte_incendios2.png')


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
from mpl_toolkits.basemap import Basemap, addcyclic, shiftgrid
from osgeo import gdal, osr  
from osgeo.gdalconst import *
from netCDF4 import Dataset
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.patches import PathPatch

f=open('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/valores_regiones1.bin','r')
valores_regiones=cPickle.load(f)
f.close()

f=open('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/fechas_regiones1.bin','r')
fechas_regiones=cPickle.load(f)
f.close()

#--------------Crear paleta de colores----------------------------------

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

#---------------------------------------------------------------------------

def Plot_semanal():

    resol = 'D'
    textsave = ''
    fontsize = 'x-small'

    var = 'Mapa Incendios'

    if   resol == 'D':  resolucion = 'Diaria'       ; datesize = 1
    elif resol == '8h': resolucion = 'Octohoraria'  ; datesize = 3
    elif resol == '1h': resolucion = 'Horaria'      ; datesize = 24
    else: pass

    f_i = fechas_regiones[0] ; f_f = fechas_regiones[len(fechas_regiones)-1]
    ticksdate = pd.date_range(str(f_i.year)+'-'+str(f_i.month)+'-'+str(f_i.day),str(f_f.year)+'-'+str(f_f.month)+'-'+str(f_f.day),freq=resol)

    path = '/home/esneider/Escritorio/Incendios_forestales/mapas/Figuras'

    how = 'mean' if var != 'PLiquida_SSR' else 'sum'
    no_in= []

    estaciones = ['1 | Barbosa','2 | Girardota','3 | Copacabana','4 | Bello','5 | Medellin centro','6 | Medellin oriente','7 | Medellin occidente','8 | Itagui','9 | Envigado','10 | La Estrella','11 | Sabaneta','12 | Caldas'][::-1]
    x = estaciones

    for est in estaciones:
        if est not in x: no_in.append(est)

    textizq=-5.6*datesize

    plt.close('all')
    fig = plt.figure(figsize=((6+ticksdate.size)*0.32, 0.42*(4+8)),facecolor='w',edgecolor='w')
    plt.subplots_adjust(wspace=.1,hspace=.3,bottom=0.1,left=0.1,right=0.90,top=0.9)

    ax={}
    i=0
    ax[i]= fig.add_subplot(111)
    plt.setp(ax[i].spines.values(), color=(0.45, 0.45, 0.45))
    ax[i].tick_params(axis=u'both', which=u'both',length=0, colors=(0.45, 0.45, 0.45))

    ax[0].set_xlim(textizq-0.5,ticksdate.size+1)
    ax[0].set_xticklabels('')
    ax[0].set_yticklabels('')

    # Contorno
    #df = np.zeros((12,7))
    #lim1 = 0.22 ; lim2 = 0.42 ; lim3 = 0.62 ; lim4 = 0.82

    #for kk in range(12):
    #    for xx in range(7):
    #        if (valores_regiones[kk][xx] >= lim1) and (valores_regiones[kk][xx] < lim2):
    #            df[kk][xx] = 1.125
    #        if (valores_regiones[kk][xx] >= lim2) and (valores_regiones[kk][xx] < lim3):
    #            df[kk][xx] = 1.875
    #        if (valores_regiones[kk][xx] >= lim3) and (valores_regiones[kk][xx] < lim4):
    #            df[kk][xx] = 2.625

    df = valores_regiones
    df = df[::-1]
    contf = ax[0].imshow(df, interpolation='nearest', cmap=rvb, vmin=0.0, vmax=0.87, aspect='auto', origin='lower', extent=[0,ticksdate.size,0,12], alpha=0.75)

    # Lineas blancas
    for i in range(len(estaciones)):
        ax[0].text(textizq,i+0.45,estaciones[i],ha='left',va='center',fontsize=fontsize)#,fontproperties=prop_1)
        ax[0].axhline(i,color='w',lw=1)

    ax[0].axhline(len(estaciones)+1,xmin=np.abs(textizq-0.5)/(ticksdate.size+1+np.abs(textizq-0.5)), xmax=(ticksdate.size+np.abs(textizq-0.5))/(ticksdate.size+1+np.abs(textizq-0.5)),color='k',lw=2.5)
    ax[0].text(textizq,12.6,u'Municipios',ha='left',va='center',fontsize='small')#,fontproperties=prop_2)

    # Fechas
    dias = ['L','M','Mi','J','V','S','D']
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    for j in range(ticksdate.size):
        strday = dias[fechas_regiones[j].weekday()]+str(fechas_regiones[j].day)
        strmes = meses[fechas_regiones[j].month - 1]
        ax[0].text(j+0.5,9+4.5,strday,fontsize='xx-small',ha='center',va='center')#,fontproperties=prop_2)
        ax[0].axvline(x=j+0.03,ymax=(len(estaciones)+.7)/(len(estaciones)+4.),color='w',lw=1) #ymin= 1./(len(estaciones)+4.)
        if ((j==0) & (ticksdate[1].day!=1)) | (ticksdate[j].day ==1) : ax[0].text(j+1, 9+5.1,strmes,ha='left',va='bottom',fontsize=fontsize)#,fontproperties=prop_2)

    ax[0].axhspan(6+8,9+6,xmin=np.abs(textizq-0.5)/(ticksdate.size+1+np.abs(textizq-0.5)), xmax=(ticksdate.size+np.abs(textizq-0.5))/(ticksdate.size+1+np.abs(textizq-0.5)),fc=(0.875,0.875,0.875),ec='w')
    ax[0].axhspan(6+8,9+6,xmax=np.abs(textizq-0.5)/(ticksdate.size+1+np.abs(textizq-0.5))-.02,fc=(0.875,0.875,0.875),ec='w')
    ax[0].text(textizq,9+5.1,var,ha='left',va='bottom',fontsize='small')#,fontproperties=prop_2)
    ax[0].text(0,6+6.5,u'SUSCEPTIBILIDAD',ha='left',va='center',fontsize=fontsize)#,fontproperties=prop_1)
    ax[0].axhline(6+6.15,xmin =0.5/(ticksdate.size+1+np.abs(textizq-0.5)),xmax=(ticksdate.size+np.abs(textizq-0.5))/(ticksdate.size+1+np.abs(textizq-0.5)),color=(0.45, 0.45, 0.45),lw=1)

    ax[0].set_ylim(-.5,len(estaciones)+3.5)
    ax[0].set_xlim(textizq-0.5,ticksdate.size+1)
    ax[0].set_xticklabels('')
    ax[0].set_yticklabels('')

    plt.savefig('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/reportes/reporte_semanal.pdf',bbox_inches='tight')

Plot_semanal()


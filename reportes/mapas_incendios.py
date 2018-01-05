
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

#--------------Crear paleta de colores----------------------

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

#----------------------------------------------------------

def Plot_Mapa4(mapa):

    figsize = 11
    fontsize = 15

    plt.close('all')
    fig = plt.figure(figsize=(figsize,figsize*(6.515-5.975)/(75.725-75.21)),facecolor='w',edgecolor='w')
    ax={}
    ax[0]= fig.add_axes((0.00,0.00,1,1))    #Relieve
    ax[3]= fig.add_axes((0.46,0.00,0.54,0.3))#Fondo Mapas Pequenos
    ax[4]= fig.add_axes((0.48,0.0,0.25,0.25))#Mapa izquierda
    ax[5]= fig.add_axes((0.75,0.0,0.25,0.25))#Mapa derecha
    ax[2]= fig.add_axes((0.0,0.91,0.35,0.09))#Fondo Colorbar
    ax[6]= fig.add_axes((0.0,0.97,0.33,0.03))#Colorbar

    for i in ax.keys():
        plt.setp(ax[i].spines.values(), color='w') #(0.45, 0.45, 0.45))
        if i > 0: ax[i].tick_params(labelleft='off',labelbottom='off',right='off',left='off',bottom='off',top='off',which='both', colors=(0.45, 0.45, 0.45))

    m = Basemap(ax=ax[0],projection='merc',llcrnrlat=5.975,urcrnrlat=6.515,llcrnrlon=-75.725,urcrnrlon=-75.21,resolution='h') # area_thresh=10000, suppress_ticFalse)
    m.drawparallels(np.linspace(6.,6.4,5),labels=[1,0,0,0],fmt="%.1f",color=(0.45, 0.45, 0.45),fontsize=fontsize,zorder=1,ax=ax[0],alpha=1,rotation='vertical',linewidth=0.1)
    m.drawmeridians(np.linspace(-75.5,-75.2,4),labels=[0,0,1,0], fmt="%.1f",color=(0.45, 0.45, 0.45),fontsize=fontsize,zorder=2,ax=ax[0],alpha=1,linewidth=0.1)

    print 'Empieza '+mapa
    if mapa =='A':
        mm = 'mapa_susc_agre.tif'
    if mapa == 'D':
        mm = 'mapa_susc_dist.tif'

    DataSet = gdal.Open('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/'+mm) #mapa agregado
    GeoTransform = DataSet.GetGeoTransform()
    longitudes=np.array([GeoTransform[0]+0.5*GeoTransform[1]+i*GeoTransform[1] for i in range(DataSet.RasterXSize)])
    latitudes=np.array([GeoTransform[3]+0.5*GeoTransform[-1]+i*GeoTransform[-1] for i in range(DataSet.RasterYSize)])
    DEM=DataSet.ReadAsArray()
    DEM[DEM==-9999]= np.NaN
    X,Y= np.meshgrid(longitudes,latitudes)
    Xm,Ym= m(X,Y)

    
###nuevo
    
    DEMmask=np.ma.masked_where(DEM==0,DEM)
    DEMmask1=np.ma.masked_where(DEM!=0,DEM)
    cmap1 = mcolors.ListedColormap(['darkslategray'])
    
    if mapa =='A':
        cs = m.contourf(Xm, Ym, DEM, levels=np.linspace(-0.01,0.87,100), cmap=rvb,alpha=.9,vmin=0.0, vmax=0.87,extend='min',zorder=3)
    if mapa == 'D':
        
        cs = m.contourf(Xm, Ym, DEM, levels=np.linspace(-0.01,0.87,100), cmap=rvb,vmin=0.0, vmax=0.87,extend='min',zorder=3,facecolor='white')
        cs1 = m.contourf(Xm, Ym, DEMmask1, levels=np.linspace(-0.01,0.87,100), cmap=cmap1,vmin=0.0, vmax=0.87,extend='min',zorder=3,facecolor='white')
      
        cs1.cmap.set_under('w')
        cs.cmap.set_under('w')
        
        #cs.set_clim(0.01)
        
    cs.cmap.set_over('k')
    cs.cmap.set_under('w')
    
    
#original

#    if mapa =='A':
#        cs = m.contourf(Xm, Ym, DEM, levels=np.linspace(-0.01,0.87,100), cmap=rvb,alpha=.9,vmin=0.0, vmax=0.87,extend='min',zorder=3)
#    if mapa == 'D':
#        cs = m.contourf(Xm, Ym, DEM, levels=np.linspace(-0.01,0.87,100), cmap=rvb,alpha=.7,vmin=0.0, vmax=0.87,extend='min',zorder=3)

#    cs.cmap.set_over('k')
#    cs.cmap.set_under('w')


    # Colorbar
    cbar= plt.colorbar(cs,cax=ax[6],orientation='horizontal',format='%.f')
    cbar.set_label("Susceptibilidad a incendios",fontsize=fontsize,color=(0.45, 0.45, 0.45))
    cbar.set_ticks([0.10,0.31,0.54,0.76])
    cbar.set_ticklabels(['Nula','Baja','Media','Alta'])
    cbar.ax.tick_params(labelsize=fontsize,colors=(0.45, 0.45, 0.45))

    m.readshapefile('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/reportes/Tools/AreaMetropolitana','Area',linewidth=0.5,color=(0.0078,0.227,0.26),zorder=4)

    # Scatter
    zor,c = 6,0
    Xcentro = [-75.32764435, -75.4474411 , -75.50104523, -75.58692932, -75.57434845, -75.51636505, -75.65366364, -75.61810303, -75.56996918, -75.65092468, -75.60826111, -75.61592102]
    Ycentro = [6.44119596,  6.37883759,  6.34711123,  6.35586309,  6.24974442, 6.23442841,  6.24536848,  6.17972755,  6.14690733,  6.13542032, 6.13924932,  6.0643096]
    region = ['1.Barbosa','2.Girardota','3.Copacabana','4.Bello','5.Medellin centro','6.Medellin oriente','7.Medellin occidente','8.Itagui','9.Envigado','10.La estrella','11.Sabaneta','12.Caldas'] 

    Xc, Yc	= m(Xcentro,Ycentro)
    m.scatter(Xc,Yc,s=700,facecolor=(0.0078,0.227,0.26),edgecolor=(0.0078,0.227,0.26),lw=1,alpha=1,zorder=5)
    for j in range(12):
        ax[0].text(Xc[j],Yc[j],region[j].split('.')[0], ha='center',va='center', fontsize=fontsize,color='w',zorder=zor)
        zor=zor+1

    print 'Colombia'
    # Colombia

    m = Basemap(ax=ax[4],projection='merc',llcrnrlat=-5,urcrnrlat=13,llcrnrlon=-81.86,urcrnrlon=-65,resolution='h')
    m.drawmapboundary(fill_color=[ 0.69019608,  0.89411765,  1.        ],zorder=1)
    m.fillcontinents(color=[ 0.96470588,  0.95686275,  0.95294118],lake_color=[ 0.69019608,  0.89411765,  1.        ],zorder=2)
    m.drawcountries(color=(0.0078,0.227,0.26),zorder=3)
    m.drawcoastlines(color=(0.0078,0.227,0.26),zorder=4)
    m.readshapefile('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/reportes/Tools/Antioquia','Antioquia',linewidth=0.1,color=(0.0078,0.227,0.26),zorder=5)
    patches = []
    for info,shape in zip(m.Antioquia_info,m.Antioquia):
        patches.append( Polygon(np.array(shape),True))

    ax[4].add_collection(PatchCollection(patches, facecolor=[ 0.64705882,  0.97647059,  0.69411765], edgecolor=(0.0078,0.227,0.26), linewidths=.1, zorder=6))

    ###########################################################################
    print 'Antioquia'
    # Antioquia
    m = Basemap(ax=ax[5],projection='merc',llcrnrlat=5.35,urcrnrlat=8.95,llcrnrlon=-77.18,urcrnrlon=-73.76,resolution='f')
    m.drawmapboundary(fill_color=[ 0.69019608,  0.89411765,  1.        ],zorder=1)
    m.fillcontinents(color=[ 0.96470588,  0.95686275,  0.95294118],lake_color=[ 0.69019608,  0.89411765,  1.        ],zorder=2)

    m.readshapefile('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/reportes/Tools/Departamentos','Departamentos',linewidth=0.1,color=(0.0078,0.227,0.26),zorder=3)
    m.readshapefile('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/reportes/Tools/Antioquia','Antioquia',linewidth=0.1,color=(0.0078,0.227,0.26),zorder=4)
    patches = []
    for info,shape in zip(m.Antioquia_info,m.Antioquia):
        patches.append( Polygon(np.array(shape),True))

    ax[5].add_collection(PatchCollection(patches, facecolor=[ 0.64705882,  0.97647059,  0.69411765], edgecolor=(0.0078,0.227,0.26), linewidths=.1,zorder=5 ))

    m.readshapefile('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/reportes/Tools/AreaMetropolitana','Area',linewidth=0.5,color=(0.0078,0.227,0.26),zorder=6)
    patches = []
    for info,shape in zip(m.Area_info,m.Area):
        patches.append( Polygon(np.array(shape),True))

    ax[5].add_collection(PatchCollection(patches, facecolor= [ 0.96470588,  0.95686275,  0.95294118], edgecolor=(0.0078,0.227,0.26), linewidths=.1,zorder=7 )) #fc=[0.21,0.60,0.65]

    print 'Saving'
    print '-------------------------------'
    if mapa =='A':
        plt.savefig('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/reportes/'+'Mapa_'+mapa+'.pdf',bbox_inches='tight')
    if mapa =='D':
        plt.savefig('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/reportes/'+'Mapa_'+mapa+'.png',bbox_inches='tight')

Plot_Mapa4('D')
Plot_Mapa4('A')

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

def hr_func(ts):
    return ts.hour

try:
    #-----------------------------------
    #Reporte por regiones ultimos 7 dias
    #-----------------------------------

    print '------------------------------'
    print 'Empieza reporte ultimos 7 dias'

    path_tif='/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/scripts/ZonasPronostico.tif'
    cu = wmf.SimuBasin(rute='/media/nicolas/Home/nicolas/01_SIATA/nc_cuencas/Cuenca_AMVA_Barbosa_C.nc') #Leer la cuenca

    mapa_zonas,prop=wmf.read_map_raster(path_tif) #Leer mapa de zonas para pronostico
    zonas_basin = cu.Transform_Map2Basin(mapa_zonas, prop) #Escribir el mapa en forma de cuenca
    zonas_basin[zonas_basin < 0] = 0
    
    historia=[]
    path='/media/nicolas/Home/Jupyter/Sebastian/Incendios/reportes/repo/'

    hdr='/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/historial.hdr'
    header=pd.read_table(hdr,sep=',',header=0,skiprows=5)
    hora_actual=pd.datetime.now()
    rec=header[' Record'][(pd.to_datetime(header[' Fecha '])<=hora_actual)&(pd.to_datetime(header[' Fecha '])>=hora_actual-dt.timedelta(days=7))&(pd.to_datetime(header[' Fecha ']).apply(hr_func)==hora_actual.hour)]
    recdias=header[' Fecha '][(pd.to_datetime(header[' Fecha '])<=hora_actual)&(pd.to_datetime(header[' Fecha '])>=hora_actual-dt.timedelta(days=7))&(pd.to_datetime(header[' Fecha ']).apply(hr_func)==hora_actual.hour)]
    recdias=recdias.tolist()
    mapas=wmf.cu.read_int_basin('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/historial.bin',rec,cu.ncells)
    
    mapas=mapas/1000.
    dias=[]
    for ii in recdias:
        ii=pd.to_datetime(ii)
        dias.append(dt.datetime(int(ii.year),int(ii.month),int(ii.day),int(ii.hour),0))

except:
    pass


day = dt.datetime.now()
day1 = day - dt.timedelta(days=6)
date = pd.date_range(str(day1.year)+'-'+str(day1.month)+'-'+str(day1.day),str(day.year)+'-'+str(day.month)+'-'+str(day.day),freq='D')
dates = []

resumen = np.zeros((12,7))

ult_hora = day.hour


for d in range(len(date)):
    date1 = dt.datetime(date[d].year, date[d].month, date[d].day, int(day.hour), 0)
    print date1
    dates.append(date1)
    datos_dh =  np.array(mapas[d])
    
    for i in np.arange(1,13,1):
        pp = np.where(np.array(zonas_basin) == i)[0]
        datos_zona = datos_dh[pp]
        hist=np.histogram(datos_zona,[0,0.22,0.42,0.62,0.87])
        posmoda=np.where(hist[0]==max(hist[0]))[0]
        moda=[0.14,0.34,0.54,0.73][posmoda[0]]#hist[1][posmoda+1]
        resumen[i-1][d] = moda
    
#print dates
f=open('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/valores_regiones1.bin','w')
cPickle.dump(resumen,f)
f.close()

f=open('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/fechas_regiones1.bin','w')
cPickle.dump(dates,f)
f.close()

#------------------------------------
#Reporte por regiones ultimas 6 horas
#------------------------------------

print '-------------------------------'
print 'Empieza reporte ultimas 6 horas'

path_tif='/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/scripts/ZonasPronostico.tif'

rec=header[' Record'][(pd.to_datetime(header[' Fecha '])<=hora_actual)&(pd.to_datetime(header[' Fecha '])>=hora_actual-dt.timedelta(hours=6))]
rechoras=header[' Fecha '][(pd.to_datetime(header[' Fecha '])<=hora_actual)&(pd.to_datetime(header[' Fecha '])>=hora_actual-dt.timedelta(hours=6))]
rechoras=rechoras.tolist()
mapas=wmf.cu.read_int_basin('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/historial.bin',rec,cu.ncells)

mapas=mapas/1000.
horas=[]

for ii in rechoras:
    ii=pd.to_datetime(ii)
    horas.append(dt.datetime(int(ii.year),int(ii.month),int(ii.day),int(ii.hour),0))

    
mapa_zonas,prop=wmf.read_map_raster(path_tif) #Leer mapa de zonas para pronostico
zonas_basin = cu.Transform_Map2Basin(mapa_zonas, prop) #Escribir el mapa en forma de cuenca
zonas_basin[zonas_basin < 0] = 0

fecha = [] ; reporte_regiones = {}
hora = dt.datetime.now()
corte = hora - dt.timedelta(hours=7)

for d in range(len(horas)):
    hora1 = dt.datetime(horas[d].year, horas[d].month, horas[d].day, int(horas[d].hour), 0)
    print hora1
    fecha.append(hora1)
    datos_hora =  np.array(mapas[d])
    all_muni = []
        
    for j in range(1,13,1):
        pp = np.where(np.array(zonas_basin) == j)[0]
        something=np.array(datos_hora)[pp]
        hist=np.histogram(something,[0,0.22,0.42,0.62,0.87])
        posmoda=np.where(hist[0]==max(hist[0]))[0]#
        if j<=6:
            moda=[0.14,0.34,0.54,0.73][posmoda[0]]+.01*j-.05 
            #moda=hist[1][posmoda+1]+.01*j-.03
        if j>6:
            moda=[0.14,0.34,0.54,0.73][posmoda[0]]+.008*j-.05 #se suma para que no se superpongan las lineas de vulnerabilidad de las ultimas 6 horas
            #moda=hist[1][posmoda+1]+.005*j-.03
        all_muni.append(moda)

    reporte_regiones[str(hora1)] = all_muni



plt.close('all')
formatter = DateFormatter ('%H:%M\n')
fig=plt.figure(edgecolor='w',facecolor='w',figsize=(15,20))
regionesXplot = np.zeros((12,len(fecha)))
Regiones=['1 Barbosa','2 Girardota','3 Copacabana','4 Bello','5 Medellin centro','6 Medellin oriente','7 Medellin occidente','8 Itagui','9 Envigado','10 La Estrella','11 Sabaneta','12 Caldas']

for y in range(12):
    
    if y <= 5:
        ax1=fig.add_subplot(2,1,1)
    if y > 5:
        ax2=fig.add_subplot(2,1,2)
        
    for x in range(len(fecha)):
        regionesXplot[y][x] = reporte_regiones[str(fecha[x])][y]

    #ax.fill_between(fecha, map25, map75, facecolor='gray', interpolate=True, alpha=0.25)
    plt.plot(fecha,regionesXplot[y],lw=5,label=Regiones[y])

r1=98/255. ; g1=210/255. ; b1=221/255.
r2=63/255. ; g2=125/255. ; b2=170/255.
r3=237/255. ; g3=226/255. ; b3=20/255.
r4=214/255. ; g4=30/255. ; b4=30/255.
    
ax1.fill_between(fecha, np.ones(len(fecha))*0., np.ones(len(fecha))*0.22, facecolor=[r1,g1,b1], interpolate=True, alpha=0.1)
ax1.fill_between(fecha, np.ones(len(fecha))*0.22, np.ones(len(fecha))*0.42, facecolor=[r2,g2,b2], interpolate=True, alpha=0.2)
ax1.fill_between(fecha, np.ones(len(fecha))*0.42, np.ones(len(fecha))*0.62, facecolor=[r3,g3,b3], interpolate=True, alpha=0.15)
ax1.fill_between(fecha, np.ones(len(fecha))*0.62, np.ones(len(fecha))*0.82, facecolor=[r4,g4,b4], interpolate=True, alpha=0.15)
ax1.tick_params(labelsize = 22)
matplotlib.rcParams.update({'font.size': 22})
ax1.set_yticks([0.14,0.34,0.54,0.73])
ax1.set_yticklabels (['Nula','Baja','Media','Alta'], rotation=90, size=24)
mm = fecha[0].month ; dd = fecha[0].day
if mm < 10:
    mm = '0'+str(mm)
if dd < 10:
    dd = '0'+str(dd)
ax1.set_ylim(0.03,0.8)
ax1.set_xlim(min(fecha),max(fecha))
ax1.xaxis.set_major_formatter(formatter)
ax1.grid()
ax1.legend(loc=2)

ax2.fill_between(fecha, np.ones(len(fecha))*0., np.ones(len(fecha))*0.22, facecolor=[r1,g1,b1], interpolate=True, alpha=0.1)
ax2.fill_between(fecha, np.ones(len(fecha))*0.22, np.ones(len(fecha))*0.42, facecolor=[r2,g2,b2], interpolate=True, alpha=0.2)
ax2.fill_between(fecha, np.ones(len(fecha))*0.42, np.ones(len(fecha))*0.62, facecolor=[r3,g3,b3], interpolate=True, alpha=0.15)
ax2.fill_between(fecha, np.ones(len(fecha))*0.62, np.ones(len(fecha))*0.82, facecolor=[r4,g4,b4], interpolate=True, alpha=0.15)
ax2.tick_params(labelsize = 22)
matplotlib.rcParams.update({'font.size': 22})
ax2.set_yticks([0.14,0.34,0.54,0.73])
ax2.set_yticklabels (['Nula','Baja','Media','Alta'], rotation=90, size=24)
ax2.set_ylim(0.03,0.8)
ax2.set_xlim(min(fecha),max(fecha))
ax2.xaxis.set_major_formatter(formatter)
ax2.grid()
ax2.legend(loc=2)
plt.savefig('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/reportes/reporte_6horas.png',bbox_inches='tight')

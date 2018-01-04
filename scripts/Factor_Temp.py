
# coding: utf-8

# In[20]:


import MySQLdb
get_ipython().magic(u'matplotlib inline')
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
from matplotlib.dates import DateFormatter


# In[42]:


# Cargar historia de maximos

f=open('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/maximos_temp.bin','r')
serie_maximos=cPickle.load(f)
f.close()


# In[43]:


# Consultar ultimo dia

estaciones = ['205','203','202','206','204','68', '201','207','73', '82', '83', '84', '105', '122']
#estaciones = ['83', '84', '105', '122']
elevacion  = [ 1463, 1472, 2781, 1766, 1334, 1475, 1477, 2366, 1659,1452, 1353, 1877, 1791, 1735,  2056]
path='/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/'

datel = datetime.datetime.now()
datel = datetime.datetime(int(datel.year),int(datel.month),int(datel.day),0,0)
#datel = datetime.datetime(2018,1,3,18,0)

date_fin = datel + datetime.timedelta(days=1)
date_ini = datel

est_maximos = [] ; dat_maximos = []

for est in estaciones:
    print est
    estacion = int(est)

    # open database connection
    host      ='192.168.1.74'
    user      ='usrCalidad'
    passw     ='aF05wnXC;'
    bd_nombre ='siata'


    datos_p = "SELECT DATE_FORMAT(fecha,'%Y-%m-%d'), DATE_FORMAT(hora, '%H:%i:%s'),ta,ua,pa,sm,dm,calidad FROM vaisala WHERE cliente = "+str(estacion)+" and fecha>='"+str(date_ini.year)+"-"+str(date_ini.month)+"-"+str(date_ini.day)+"' and fecha<='"+str(date_fin.year)+"-"+str(date_fin.month)+"-"+str(date_fin.day)+"'"                                                                                                                                                                                                                                                                                                                                                                                                                                                       
    db = MySQLdb.connect(host, user,passw,bd_nombre)
    db_cursor = db.cursor()
    db_cursor.execute(datos_p)
    data2 = db_cursor.fetchall()

    date2=[] ; ta=[]
    
    for i in data2:

        if (i[7] < 100) and (float(i[2]) != 0):
            try:
                date2.append(datetime.datetime(int(i[0][0:4]),int(i[0][5:7]),int(i[0][8:11]),int(i[1][0:2]),int(i[1][3:5])))

                try:
                    ta.append(float(i[2])/10.)
                except:
                    ta.append(np.nan)
            except:
                pass
    try:        
        mm = np.where(np.array(ta) == max(ta))[0][0]
        dat_maximos.append(date_ini)
        est_maximos.append(max(ta))
    except:
        dat_maximos.append(date_ini)
        est_maximos.append(0)
        pass


# In[44]:


def var2sandarize(var,method='std',rango=None):
    if method=='std':
        var=(var-var.mean())/var.std()
    if method=='minmax':
        var=(var-var.min())/(var.max()-var.min())
        if rango<>None:
            var=var*(rango[1]-rango[0])+rango[0]
    return var


# In[45]:


serie_ori_total = [] ; serie_date_total = []

for ser_ori,ult_dato,ser_date in zip(serie_maximos['serie_est_original'],est_maximos,serie_maximos['serie_est_date']):
    so = list(np.copy(ser_ori))
    so.append(ult_dato)
    serie_ori_total.append(so)
    
    sd = list(np.copy(ser_date))
    sd.append(date_ini)
    serie_date_total.append(sd)


# In[46]:


date1 = datetime.datetime(2017,7,1,0,0)
date2 = date_ini
    
fec_dd = date1
fec_freq = []

while fec_dd <= date2:
    fec_freq.append(fec_dd + datetime.timedelta(days=1))
    fec_dd = fec_dd + datetime.timedelta(days=1)


# ## Grafico de estandarizadas totales

# In[47]:


import matplotlib

#-----------------------------------------------
# Incendios reportados en la ventana analizada
#-----------------------------------------------

reportados=np.loadtxt('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/registro.csv',delimiter=',',usecols=(1,2,3,4,5),dtype='str')
date_r = []
for r in range(1,len(reportados),1):
    yy = int(reportados[r][4].split('-')[0])
    mm = int(reportados[r][4].split('-')[1])
    dd = int(reportados[r][4].split('-')[2])
    aux = datetime.datetime(yy,mm,dd)
    
    if aux >= date1:
        date_r.append(aux)

#-------------------------------------------------
        
plt.close('all')
fig = plt.figure(figsize=(20,15),facecolor='w',edgecolor='w')

resumen_std = []

for d,m in zip(serie_date_total, serie_ori_total):
    m_std = var2sandarize(np.array(m))
    resumen_std.append(m_std)
    plt.plot(d,m_std,lw=0.8,alpha=0.6)
    
dato = []

for f in fec_freq:
    aux = []
    
    for d,t,e in zip(serie_date_total,resumen_std,estaciones):
        n_dias = [x.days for x in np.array(d)-f]
        aa = np.where(np.array(n_dias) == 0)[0]
        if len(aa) > 0:
            aux.append(np.array(t)[aa][0])
    
    if len(aux) > 1 : dato.append(np.percentile(aux,50))

plt.plot(fec_freq[0:-1],dato,lw=3,c='k')
plt.scatter(fec_freq[0:-1],dato,s=30,color='k')
matplotlib.rcParams.update({'font.size': 15})

# Agregar incendios reportados

inc_dato = []

for inc in date_r:
    ii = np.where(np.array(fec_freq[0:-1]) == inc)[0]
    plt.scatter(inc,np.array(dato)[ii],s=80,color='r')
    inc_dato.append(np.array(dato)[ii][0])

plt.grid(linestyle='--')
plt.fill_between(fec_freq[0:-1],-4,np.percentile(inc_dato,5),color='blue', alpha=0.05,label='Probabilidad baja')
plt.fill_between(fec_freq[0:-1],np.percentile(inc_dato,5),np.percentile(inc_dato,30),color='orange', alpha=0.05,label='Probabilidad media')
plt.fill_between(fec_freq[0:-1],np.percentile(inc_dato,30),4,color='red', alpha=0.05,label='Probabilidad Alta')
plt.xlim(date1+datetime.timedelta(hours=8),date2+datetime.timedelta(hours=4))
#plt.xlim(date_fin-datetime.timedelta(days=30),date_fin+datetime.timedelta(hours=4))
plt.legend()
plt.ylim(-4,3)
plt.show()

#----------------------------------------------------------------------------

plt.close('all')
fig = plt.figure(figsize=(20,15),facecolor='w',edgecolor='w')

resumen_std = []

for d,m in zip(serie_date_total, serie_ori_total):
    m_std = var2sandarize(np.array(m))
    resumen_std.append(m_std)
    plt.plot(d,m_std,lw=0.8,alpha=0.6)
    
dato = []

for f in fec_freq:
    aux = []
    
    for d,t,e in zip(serie_date_total,resumen_std,estaciones):
        n_dias = [x.days for x in np.array(d)-f]
        aa = np.where(np.array(n_dias) == 0)[0]
        if len(aa) > 0:
            aux.append(np.array(t)[aa][0])
    
    if len(aux) > 1 : dato.append(np.percentile(aux,50))

plt.plot(fec_freq[0:-1],dato,lw=3,c='k')
plt.scatter(fec_freq[0:-1],dato,s=30,color='k')
matplotlib.rcParams.update({'font.size': 15})

# Agregar incendios reportados

inc_dato = []

for inc in date_r:
    ii = np.where(np.array(fec_freq[0:-1]) == inc)[0]
    plt.scatter(inc,np.array(dato)[ii],s=80,color='r')
    inc_dato.append(np.array(dato)[ii][0])

plt.grid(linestyle='--')
plt.fill_between(fec_freq[0:-1],-3,np.percentile(inc_dato,5),color='blue', alpha=0.05,label='Probabilidad baja')
plt.fill_between(fec_freq[0:-1],np.percentile(inc_dato,5),np.percentile(inc_dato,30),color='orange', alpha=0.05,label='Probabilidad media')
plt.fill_between(fec_freq[0:-1],np.percentile(inc_dato,30),3,color='red', alpha=0.05,label='Probabilidad Alta')
#plt.xlim(date_ini+datetime.timedelta(hours=8),date_fin+datetime.timedelta(hours=4))
plt.xlim(date2-datetime.timedelta(days=30),date2+datetime.timedelta(hours=4))
plt.legend()
plt.ylim(-3,3)
plt.show()


# ## Definir en que region se ubica el dia actual

# In[48]:


ult_std = dato[len(dato)-1]

if ult_std > np.percentile(inc_dato,30) : region = 'alta'
if ult_std < np.percentile(inc_dato,5) : region = 'baja'
if (ult_std >= np.percentile(inc_dato,5)) and (ult_std <= np.percentile(inc_dato,30)) : region = 'media'

print region


# ## Guardar archivo definitivo del dia

# In[49]:


yy = datel.year ; mm = datel.month ; dd = datel.day

fecha_corte = datetime.datetime(yy,mm,dd,17,0)

if datetime.datetime.now() > fecha_corte:
    print 'Ya se registro el maximo del dia'

    serie_maximos = {}

    serie_maximos['serie_est_date'] = serie_date_total
    serie_maximos['serie_est_original'] = serie_ori_total

    f=open('/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/operacional/maximos_temp.bin','w')
    cPickle.dump(serie_maximos,f)
    f.close()


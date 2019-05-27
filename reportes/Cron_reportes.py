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

path='/media/nicolas/Home/Jupyter/Esneider/incendios_forestales/reportes/'

#Generar reportes
print '                                           '
print '--------- Generar reportes ------------------'
print '                                           '

comando = 'python '+path+'generar_reportes.py'
os.system(comando)

#Mapa incendios              
print '                                           '
print '--------- Mapas incendios ------------------'
print '                                           '

comando = 'python '+path+'mapas_incendios.py'
os.system(comando)

#Reporte semanal              
print '                                           '
print '--------- Reporte semanal ------------------'
print '                                           '

comando = 'python '+path+'reporte_semanal.py'
os.system(comando)

#Composicion              
print '                                           '
print '--------- Composicion ------------------'
print '                                           '

comando = 'python '+path+'composicion.py'
os.system(comando)

os.system('sshpass -p "1037646272" scp /media/nicolas/Home/Jupyter/Esneider/incendios_forestales/reportes/Reporte_incendios2.png seospina@siata.gov.co:/var/www/seospina/')
os.system('sshpass -p "1037646272" scp /media/nicolas/Home/Jupyter/Esneider/incendios_forestales/reportes/Reporte_incendios1.png seospina@siata.gov.co:/var/www/seospina/')

#!/bin/env python
import netCDF4 as nc
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from glob import glob
import sys
import datetime as dt
import importlib

if len(sys.argv) != 3:
  print 'wrong usage:'
  print 'plot.py <res(l/h)> <path to wrfout files>'
  sys.exit(1)

sourceDir = sys.argv[2]
outputDir = sourceDir
res = sys.argv[1]
if res == 'h':
  inputFile = glob(sourceDir+'/wrfout_d02_????-??-??_??:??:??')[0]
  plot_domain = 'd02'
else:
  inputFile = glob(sourceDir+'/wrfout_d01_????-??-??_??:??:??')[0]
  plot_domain = 'd01'



#--------------
# initialization

# load in all the plotting plugins
plugins=[]
for p in glob('plot_plugins/[a-zA-Z]*py'):
  md='plot_plugins.'+p.split('/')[-1].split('.')[0]
  plugins.append(importlib.import_module(md))

#read in information about the domains
ncd = nc.Dataset(inputFile)
pncd = nc.Dataset(inputFile+'_INTRP')
domain={}
domain['start'] = dt.datetime.strptime(ncd.START_DATE,"%Y-%m-%d_%H:%M:%S")
lats  = ncd.variables['XLAT'][0]
lons  = ncd.variables['XLONG'][0]
pltenv={}

if res =='h':
  m= Basemap(width=600000, height=400000, rsphere=(6378137.00,6356752.3142),
            resolution='h',area_thresh=1000.,projection='lcc',
            lat_1=39,lat_2=39,lat_0=39,lon_0=-77.5)
  stationFile = '/home/wrf/scripts/stations.toplot'
  stations = np.genfromtxt(stationFile,delimiter=',',skip_header=2,dtype='str')
  station_lat = stations[:,0]
  station_lon = stations[:,1]
  station_code = stations[:,2]
  slon,slat = m(station_lon,station_lat)
  pltenv['slon'] = slon
  pltenv['slat'] = slat
  pltenv['station_code'] = station_code


else:
  m= Basemap(width=4300000, height=3100000, rsphere=(6378137.00,6356752.3142),
            resolution='l',area_thresh=1000.,projection='lcc',
            lat_1=37.5,lat_2=37.5,lat_0=37.5,lon_0=-84.)
  
            
x,y = m(lons,lats)

pltenv['map'] = m
pltenv['x'] = x
pltenv['y'] = y

#TODO
# get the correct number of timesteps
# read the timestamp from the file instead of the harcoded mehtod here

#-------------
# plot plugins
for p in plugins:
  for timestep in range(len(ncd.variables['Times'])+1):
    if ( timestep % p.frequency) > 0:
      continue
    print '{0} {1:03d}'.format(p.filename,timestep)
    fig = plt.figure(figsize=(14,11))
    ax=fig.add_axes([0.03,0.1,0.94,0.8])
    pltenv['ax']=ax
  
    ctime = domain['start'] + dt.timedelta(hours=timestep)

    #annotations, boundaries, etc
    ax.annotate('init:  '+domain['start'].strftime('%Y-%m-%d %HZ'),xy=(1,1.03),fontsize=9,
              xycoords="axes fraction", horizontalalignment='right')
    ax.annotate('valid: '+ctime.strftime('%Y-%m-%d %HZ'),xy=(1,1.01),fontsize=9,
              xycoords="axes fraction", horizontalalignment='right')
    ax.annotate('University of Maryland Dept. of Atmospheric and Oceanic Science',
              xy=(1.01,0), xycoords=('axes fraction'),rotation=90,horizontalalignment='left',verticalalignment='bottom',
              color='gray',fontsize=8)
    ax.annotate('EXPERIMENTAL', xy=(0,1.01), xycoords=('axes fraction'), horizontalalignment='left',
              verticalalignment='bottom', color='red')

    pltenv['map'].drawcoastlines(color= p.boundaryColor)
    pltenv['map'].drawcountries(color=p.boundaryColor)
    pltenv['map'].drawstates(color=p.boundaryColor)
       
    plt.title(p.title,fontweight='bold')
    
    p.plot(ncd.variables,pncd.variables, pltenv, timestep)
    
    if res == 'h':

       m.plot(pltenv['slon'], pltenv['slat'], 'ko', markersize=10)

       labels =  pltenv['station_code']
       for label, xpt, ypt in zip(labels, pltenv['slon'], pltenv['slat']):
           plt.text(xpt+1000, ypt+2500, label)

    else: 
       pass 

    #colorbar
    #TODO, move this to sub routines
    pos = ax.get_position()
    l, b, w, h = pos.bounds
    ch = 0.015
    cw = 0.8
    cax=plt.axes([l + w*(1-cw)/2,b-ch-0.005,w*cw,ch])
    cb = plt.colorbar(cax=cax, orientation='horizontal')


    plt.savefig(outputDir+'/{0}_F{1:03d}_{2}.png'.format(p.filename,timestep,plot_domain))
    plt.close('all')

#!/usr/bin/env python
"""
meteogram.py
Python script to plot meteograms for TerpWRF
C. Martin - 3/1/2016
"""
import netCDF4 as nc
import matplotlib as mpl; mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from glob import glob
import sys
import datetime as dt

if len(sys.argv) != 4:
  print 'wrong usage:'
  print 'meteogram.py <res(l/h)> <path to wrfout files> <path to station file>'
  sys.exit(1)

res = sys.argv[1]
sourceDir = sys.argv[2]
outputDir = sourceDir
stationFile = sys.argv[3]

if res == 'h':
  inputFile = glob(sourceDir+'/wrfout_d02_????-??-??_??:??:??')[0]
  plot_domain = 'd02'
else:
  inputFile = glob(sourceDir+'/wrfout_d01_????-??-??_??:??:??')[0]
  plot_domain = 'd01'

#---------------------
# read in the station file
stations = np.genfromtxt(stationFile,delimiter=',',skip_header=2,dtype='str')
station_lat = stations[:,0]
station_lon = stations[:,1]
station_code = stations[:,2]
station_name = stations[:,3]

# read in data from netCDF files
ncd = nc.Dataset(inputFile)
pncd = nc.Dataset(inputFile+'_INTRP')
domain={}
domain['start'] = dt.datetime.strptime(ncd.START_DATE,"%Y-%m-%d_%H:%M:%S")
lats  = ncd.variables['XLAT'][0] 
lons  = ncd.variables['XLONG'][0]

# function to get lat/lon point
from math import pi
def findpoint(latvar,lonvar,lat0,lon0):
    '''
    Find closest point in a set of (lat,lon) points to specified point
    latvar - 2D latitude variable from an open netCDF dataset
    lonvar - 2D longitude variable from an open netCDF dataset
    lat0,lon0 - query point
    Returns iy,ix such that the square of the tunnel distance
    between (latval[it,ix],lonval[iy,ix]) and (lat0,lon0)
    is minimum.
    From Unidata python workshop
    '''
    rad_factor = pi/180.0 # for trignometry, need angles in radians
    # Read latitude and longitude from file into numpy arrays
    latvals = latvar[:] * rad_factor
    lonvals = lonvar[:] * rad_factor
    ny,nx = latvals.shape
    lat0_rad = lat0 * rad_factor
    lon0_rad = lon0 * rad_factor
    # Compute numpy arrays for all values, no loops
    clat,clon = np.cos(latvals),np.cos(lonvals)
    slat,slon = np.sin(latvals),np.sin(lonvals)
    delX = np.cos(lat0_rad)*np.cos(lon0_rad) - clat*clon
    delY = np.cos(lat0_rad)*np.sin(lon0_rad) - clat*slon
    delZ = np.sin(lat0_rad) - slat;
    dist_sq = delX**2 + delY**2 + delZ**2
    minindex_1d = dist_sq.argmin()  # 1D index of minimum element
    iy_min,ix_min = np.unravel_index(minindex_1d, latvals.shape)
    return iy_min,ix_min

timestamps = ncd.variables['Times'][:]
timestamps = [''.join(timestamps[t]) for t in range(len(timestamps))]
timestamps = [dt.datetime.strptime(timestamps[t],'%Y-%m-%d_%H:%M:%S') for t in range(len(timestamps))]

mtemp = ncd.variables['T2'][:] + 6.5*ncd.variables['HGT'][:]/1000./2.
mslp = ncd.variables['PSFC'][:] * np.exp(9.81/(287.0*mtemp)*ncd.variables['HGT'][:])*0.01
T2 = ncd.variables['T2'][:]
U10 = ncd.variables['U10'][:]
V10 = ncd.variables['V10'][:]
U10 = U10*1.943844492 # convert to knots
V10 = V10*1.943844492 # convert to knots
T2 = ((T2 - 273.15)*1.8) + 32.
PBLH = ncd.variables['PBLH'][:]
precip = (ncd.variables['RAINNC'][:]+ncd.variables['RAINC'][:])*0.03937
Q2 = ncd.variables['Q2'][:]
# calculate Td
A = 2.53e9
B = 5.42e3
e = 0.622
Td = B / (np.log((A*e)/(Q2*mslp)))
Td = ((Td - 273.15)*1.8) + 32
# for each location specified
for a in range(len(station_code)):
  j,i = findpoint(lats,lons,float(station_lat[a]),float(station_lon[a]))
  print(lats[j,i],lons[j,i],station_code[a],station_name[a])
  fig = plt.figure(figsize=(11,8.5))

  # top panel
  ax1 = plt.subplot2grid((6, 1), (0, 0))
  ax1.grid(True)
  ax1.set_ylabel('Temp/Dew Pt. (F)',fontsize=9)
  ax1.yaxis.tick_right()
  ax1.tick_params(axis='y', which='major', labelsize=9)
  ax1.plot_date(timestamps,T2[:,j,i],color='red')
  ax1.plot_date(timestamps,Td[:,j,i],color='green')
  # second panel
  ax2 = plt.subplot2grid((6, 1), (1, 0))
  ax2.grid(True)
  ax2.set_ylabel('MSLP (mb)',fontsize=9)
  ax2.yaxis.tick_right()
  ax2.tick_params(axis='y', which='major', labelsize=9)
  ax2.plot_date(timestamps,mslp[:,j,i])
  # third panel
  ax3 = plt.subplot2grid((6, 1), (2, 0))
  ax3.set_ylabel('Wind Vector',fontsize=9)
  barbzeros = np.zeros(len(timestamps))
  barbx = np.arange(0,len(timestamps),1)
  ax3.barbs(barbx,barbzeros,U10[:,j,i],V10[:,j,i],clip_on=False)
  ax3.set_xlim([0,len(timestamps)-1])
  ax3.xaxis.set_ticks(np.arange(0,len(timestamps),6))
  ax3.yaxis.tick_right()
  ax3.tick_params(axis='y', which='major', labelsize=9)
  # fourth panel
  ax4 = plt.subplot2grid((6, 1), (3, 0))
  ax4.grid(True)
  ax4.set_ylabel('QPF to Hour (in.)',fontsize=9)
  ax4.yaxis.tick_right()
  ax4.plot_date(timestamps,precip[:,j,i])
  ax4.tick_params(axis='y', which='major', labelsize=9)
  # fifth panel
  ax5 = plt.subplot2grid((6, 1), (4, 0))
  ax5.plot_date(timestamps,PBLH[:,j,i])
  ax5.set_ylabel('PBL Height (m)',fontsize=9)
  ax5.yaxis.tick_right()
  ax5.grid(True)
  ax5.tick_params(axis='y', which='major', labelsize=9)

  # make plot look nice  
  # xticks
  for ax in [ax1,ax2,ax3,ax4]:
    plt.setp(ax.get_xticklabels(),visible=False)
  plt.setp(ax3.get_yticklabels(),visible=False)
  ax5.xaxis.set_major_formatter(mpl.dates.DateFormatter('%b%d %H:%MZ')) # sets date format of x tick labels
  plt.xticks(rotation=70)
  for tick in ax5.xaxis.get_majorticklabels():
    tick.set_horizontalalignment("right")
  ax1.annotate('Initialized:     '+domain['start'].strftime('%Y-%m-%d %HZ'),xy=(1,1.1),fontsize=9, xycoords="axes fraction", horizontalalignment='right')
  ax1.annotate(station_name[a],xy=(0,1.1),fontsize=19, xycoords="axes fraction", horizontalalignment='left')
  ax1.annotate('Model:TerpWRF Station:'+station_code[a],xy=(1,1.25),fontsize=9, xycoords="axes fraction", horizontalalignment='right')
  ax1.annotate('University of Maryland - Dept. of Atmospheric and Oceanic Science',
              xy=(0.5,0.05), xycoords=('figure fraction'),horizontalalignment='center',verticalalignment='bottom',fontsize=12)
  ax1.annotate('http://trowal.weather.umd.edu',
              xy=(0.5,0.01), xycoords=('figure fraction'),horizontalalignment='center',verticalalignment='bottom',
              color='gray',fontsize=12)
  ax1.annotate('EXPERIMENTAL', xy=(0,0.01), xycoords=('figure fraction'), horizontalalignment='left',
              verticalalignment='bottom', color='red')

  plt.savefig(outputDir+'/meteogram_{0}.png'.format(station_code[a]))


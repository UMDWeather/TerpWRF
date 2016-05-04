#!/usr/bin/env python
"""
sounding.py
Python script to plot soundings for TerpWRF
C. Martin - 3/2/2016
"""
import netCDF4 as nc
import matplotlib as mpl; mpl.use('Agg')
import matplotlib.pyplot as plt
from glob import glob 
import sys
import datetime as dt
from matplotlib.axes import Axes
import matplotlib.transforms as transforms
import matplotlib.axis as maxis
import matplotlib.spines as mspines
import matplotlib.path as mpath
from matplotlib.projections import register_projection
from matplotlib.ticker import ScalarFormatter, MultipleLocator
import numpy as np

if len(sys.argv) != 4:
  print 'wrong usage:'
  print 'sounding.py <res(l/h)> <path to wrfout files> <path to station file>'
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

U = pncd.variables['UU'][:]
V = pncd.variables['VV'][:]
U = U*1.943844492 # convert to knots
V = V*1.943844492 # convert to knots
T = pncd.variables['TT'][:]
T = T - 273.15 # convert to Celsius
RH = pncd.variables['RH'][:]
P = pncd.variables['LEV'][:]
Td = 243.04*(np.log(RH/100)+((17.625*T)/(243.04+T)))/(17.625-np.log(RH/100)-((17.625*T)/(243.04+T))) 

"""
SKEW-T crap below
"""
# The sole purpose of this class is to look at the upper, lower, or total
# interval as appropriate and see what parts of the tick to draw, if any.


class SkewXTick(maxis.XTick):
    def draw(self, renderer):
        if not self.get_visible():
            return
        renderer.open_group(self.__name__)

        lower_interval = self.axes.xaxis.lower_interval
        upper_interval = self.axes.xaxis.upper_interval

        if self.gridOn and transforms.interval_contains(
                self.axes.xaxis.get_view_interval(), self.get_loc()):
            self.gridline.draw(renderer)

        if transforms.interval_contains(lower_interval, self.get_loc()):
            if self.tick1On:
                self.tick1line.draw(renderer)
            if self.label1On:
                self.label1.draw(renderer)

        if transforms.interval_contains(upper_interval, self.get_loc()):
            if self.tick2On:
                self.tick2line.draw(renderer)
            if self.label2On:
                self.label2.draw(renderer)

        renderer.close_group(self.__name__)


# This class exists to provide two separate sets of intervals to the tick,
# as well as create instances of the custom tick
class SkewXAxis(maxis.XAxis):
    def __init__(self, *args, **kwargs):
        maxis.XAxis.__init__(self, *args, **kwargs)
        self.upper_interval = 0.0, 1.0

    def _get_tick(self, major):
        return SkewXTick(self.axes, 0, '', major=major)

    @property
    def lower_interval(self):
        return self.axes.viewLim.intervalx

    def get_view_interval(self):
        return self.upper_interval[0], self.axes.viewLim.intervalx[1]


# This class exists to calculate the separate data range of the
# upper X-axis and draw the spine there. It also provides this range
# to the X-axis artist for ticking and gridlines
class SkewSpine(mspines.Spine):
    def _adjust_location(self):
        trans = self.axes.transDataToAxes.inverted()
        if self.spine_type == 'top':
            yloc = 1.0
        else:
            yloc = 0.0
        left = trans.transform_point((0.0, yloc))[0]
        right = trans.transform_point((1.0, yloc))[0]

        pts = self._path.vertices
        pts[0, 0] = left
        pts[1, 0] = right
        self.axis.upper_interval = (left, right)


# This class handles registration of the skew-xaxes as a projection as well
# as setting up the appropriate transformations. It also overrides standard
# spines and axes instances as appropriate.
class SkewXAxes(Axes):
    # The projection must specify a name.  This will be used be the
    # user to select the projection, i.e. ``subplot(111,
    # projection='skewx')``.
    name = 'skewx'

    def _init_axis(self):
        # Taken from Axes and modified to use our modified X-axis
        self.xaxis = SkewXAxis(self)
        self.spines['top'].register_axis(self.xaxis)
        self.spines['bottom'].register_axis(self.xaxis)
        self.yaxis = maxis.YAxis(self)
        self.spines['left'].register_axis(self.yaxis)
        self.spines['right'].register_axis(self.yaxis)

    def _gen_axes_spines(self):
        spines = {'top': SkewSpine.linear_spine(self, 'top'),
                  'bottom': mspines.Spine.linear_spine(self, 'bottom'),
                  'left': mspines.Spine.linear_spine(self, 'left'),
                  'right': mspines.Spine.linear_spine(self, 'right')}
        return spines

    def _set_lim_and_transforms(self):
        """
        This is called once when the plot is created to set up all the
        transforms for the data, text and grids.
        """
        rot = 30

        # Get the standard transform setup from the Axes base class
        Axes._set_lim_and_transforms(self)

        # Need to put the skew in the middle, after the scale and limits,
        # but before the transAxes. This way, the skew is done in Axes
        # coordinates thus performing the transform around the proper origin
        # We keep the pre-transAxes transform around for other users, like the
        # spines for finding bounds
        self.transDataToAxes = self.transScale + \
            self.transLimits + transforms.Affine2D().skew_deg(rot, 0)

        # Create the full transform from Data to Pixels
        self.transData = self.transDataToAxes + self.transAxes

        # Blended transforms like this need to have the skewing applied using
        # both axes, in axes coords like before.
        self._xaxis_transform = (transforms.blended_transform_factory(
            self.transScale + self.transLimits,
            transforms.IdentityTransform()) +
            transforms.Affine2D().skew_deg(rot, 0)) + self.transAxes

# Now register the projection with matplotlib so the user can select
# it.
register_projection(SkewXAxes)

frequency = 3 # output every 3 hours

# loop through locations
for a in range(len(station_code)):
 j,i = findpoint(lats,lons,float(station_lat[a]),float(station_lon[a]))
 print(lats[j,i],lons[j,i],station_code[a],station_name[a])
 for timestep in range(len(ncd.variables['Times'])+1):
  if ( timestep % frequency) > 0:
    continue
  t = timestep
  ctime = domain['start'] + dt.timedelta(hours=timestep)
  fig = plt.figure(figsize=(11,8.5))
  ax = plt.subplot2grid((1,6),(0,0), projection='skewx',colspan=5)
  plt.grid(True)
  ax1 = plt.subplot2grid((1,6),(0,5),sharey=ax)
  ax1.axis('off')
  ax1.set_xlim([-5,5])
  # Plot the data using normal plotting functions, in this case using
  # log scaling in Y, as dicatated by the typical meteorological plot
  ax.semilogy(T[t,:,j,i], P/100., 'r')
  ax.semilogy(Td[t,:,j,i], P/100., 'g')

  # An example of a slanted line at constant X
  l = ax.axvline(0, color='b')

  # Disables the log-formatting that comes with semilogy
  ax.yaxis.set_major_formatter(ScalarFormatter())
  ax.set_yticks(np.linspace(100, 1000, 10))
  ax.set_ylim(1050, 100)

  ax.xaxis.set_major_locator(MultipleLocator(10))
  ax.set_xlim(-50, 50)

  # plot wind barbs
  zeropts = np.zeros(len(P))
  ax1.barbs(zeropts,P/100.,U[t,:,j,i],V[t,:,j,i])

  ax1.annotate('Initialized:     '+domain['start'].strftime('%Y-%m-%d %HZ'),xy=(1,1.03),fontsize=9, xycoords="axes fraction", horizontalalignment='right')
  ax1.annotate('Valid:            '+ctime.strftime('%Y-%m-%d %HZ'),xy=(1,1.01),fontsize=9, xycoords="axes fraction", horizontalalignment='right')
  ax.annotate(station_name[a],xy=(0,1.02),fontsize=19, xycoords="axes fraction", horizontalalignment='left')
  ax1.annotate('Model:TerpWRF Station:'+station_code[a],xy=(1,1.05),fontsize=9, xycoords="axes fraction", horizontalalignment='right')
  ax.annotate('University of Maryland - Dept. of Atmospheric and Oceanic Science',
              xy=(0.5,0.05), xycoords=('figure fraction'),horizontalalignment='center',verticalalignment='bottom',fontsize=12)
  ax.annotate('http://trowal.weather.umd.edu',
              xy=(0.5,0.01), xycoords=('figure fraction'),horizontalalignment='center',verticalalignment='bottom',
              color='gray',fontsize=12)
  ax.annotate('EXPERIMENTAL', xy=(0,0.01), xycoords=('figure fraction'), horizontalalignment='left',
              verticalalignment='bottom', color='red')

  plt.savefig(outputDir+'/sounding_F{0:03d}_{1}.png'.format(timestep,station_code[a])) 
  plt.close('all')

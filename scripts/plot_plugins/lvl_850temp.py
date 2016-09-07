import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndimage
from scipy.ndimage.filters import minimum_filter, maximum_filter
from mpl_toolkits.basemap import cm

filename='lvl_850temp'
title ='850mb Temperature'
cbarlabel = 'Temperature (C)'
boundaryColor = 'gray'
frequency = 3                   # frequency in hrs


def plot(variables,prev_vars,pltenv):

    cont_int = 10
    cont_smooth = 0.5
    thin = 10
    lvl = 2
    time = 0

    x = pltenv['x']
    y = pltenv['y']
    m = pltenv['map']


    bbox = dict(boxstyle="square",ec='None',fc=(1,1,1,0.75))

  
    T= variables['T_PL'][time][lvl]
    temp = T - 273.15 # convert to Celsius 
    levels = np.arange(-100,150,5)
    levels2 = np.arange(-50,50,1)

    P = m.contour(x,y,temp,levels=levels,colors='k')
    plt.clabel(P,inline=1,fontsize=10,fmt='%1.0f',inline_spacing=1)

    P = m.contour(x,y,temp,levels=[0],colors='r')
    plt.clabel(P,inline=1,fontsize=10,fmt='%1.0f',inline_spacing=1)


    m.contourf(x,y,temp, levels=levels2, extend='both')



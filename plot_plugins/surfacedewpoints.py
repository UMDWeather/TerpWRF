import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndimage
from scipy.ndimage.filters import minimum_filter, maximum_filter
from mpl_toolkits.basemap import cm

filename='surfacedewpoint'
title ='Surface Dew Point'
cbarlabel = 'Dew Point Temperature (F)'
boundaryColor = 'gray'
frequency = 3                   # frequency in hrs


def plot(variables, pvars, pltenv, time):

    cont_int = 10
    cont_smooth = 0.5

    x = pltenv['x']
    y = pltenv['y']
    m = pltenv['map']

    bbox = dict(boxstyle="square",ec='None',fc=(1,1,1,0.75))

    var=(variables['T2'][time]-273.15)
    var2=pvars['RH'][time][1]
    var3=243.04*(np.log(var2/100)+((17.625*var)/(243.04+var)))/(17.625-np.log(var2/100)-((17.625*var)/(243.04+var)))
    var4=var3*1.8+32
    levels = np.arange(-40,90,1)
    levels2 = np.arange(-100,150,cont_int)
    P = m.contour(x,y,var4,levels=levels2,colors='k')
    plt.clabel(P,inline=1,fontsize=10,fmt='%1.0f',inline_spacing=1)
    m.contourf(x,y,var4,levels=levels, cmap='gist_ncar', extend='both')
 

    

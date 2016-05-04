import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndimage
from scipy.ndimage.filters import minimum_filter, maximum_filter
from mpl_toolkits.basemap import cm

filename='lvl_850winds'
title ='850mb Winds'
boundaryColor = 'gray'
frequency = 3                   # frequency in hrs


def plot(variables, pvars, pltenv, time):

    cont_int = 10
    cont_smooth = 0.5
    thin = 10
    lvl = 6

    x = pltenv['x']
    y = pltenv['y']
    m = pltenv['map']

    u = pvars['UU'][time][lvl] * 1.94384
    v = pvars['VV'][time][lvl] * 1.94384
    mag = np.sqrt(u**2 + v**2)

    bbox = dict(boxstyle="square",ec='None',fc=(1,1,1,0.75))

    var = pvars['GHT'][time][lvl]/10
    levels = np.arange(0,400,4)
    P = m.contour(x,y,var,levels=levels,colors='k')
    plt.clabel(P,inline=1,fontsize=10,fmt='%1.0f',inline_spacing=1)



    colors = [
        "#ffffff",
        "#a4a4a4",
        "#6e6e6e",
        "#81daf5",
        "#2efef7",
        "#2effa5",
        "#00ff44",
        "#00ff15",
        "#17ab00",
        "#90e803",
        "#daff00",
        "#ffe200",
        "#f8361c",
        "#e70101",
        "#d81a3a",
        "#fa1c6a",
        "#d545ac",
        "#ce1bb6",
        "#a40268",
        "#6002a4",
        ]

    colormap = mpl.colors.ListedColormap(colors)
    levels = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,]
    norm = mpl.colors.BoundaryNorm(levels, 21)

    m.contourf(x,y, mag, levels,cmap=colormap, norm=norm)
    m.barbs(x[::thin,::thin], y[::thin,::thin], u[::thin,::thin], v[::thin,::thin], length=6)

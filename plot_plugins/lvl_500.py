import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndimage
from scipy.ndimage.filters import minimum_filter, maximum_filter
from mpl_toolkits.basemap import cm

filename='lvl_500'
title ='500mb Geopotential Height'
cbarlabel = 'Geopotential Height (dam)'
boundaryColor = 'gray'
frequency = 3                   # frequency in hrs

def plot(variables, pvars, pltenv, time):

    cont_int = 10
    cont_smooth = 0.5
    thin = 10
    lvl = 11 

    x = pltenv['x']
    y = pltenv['y']
    m = pltenv['map']

    var = pvars['GHT'][time][lvl]/10
    levels = np.arange(0,600,4)
    P = m.contour(x,y,var,levels=levels,colors='k')
    plt.clabel(P,inline=1,fontsize=10,fmt='%1.0f',inline_spacing=1)

    colors = [
        "#f7dfe3",
        "#f6ced8",
    	"#f781be",
        "#f781f3",
        "#be81f7",
        "#58d3f7",
        "#0080ff",
        "#013adf",
        "#0404b4",
        "#0093a3",
        "#0fb586",
        "#0b614b",
        "#24ba42",
	"#c2f31e",
	"#ffff00",
	"#ffe600",
	"#ffb300",
	"#ff8d00",
	"#da5f13",
	"#e3241d",
	"#a62925",
	"#641c19",
	"#190303",
        ]
    colormap = mpl.colors.ListedColormap(colors)
    levels = [504, 508, 512, 516, 520, 524, 528, 532, 536, 540, 544, 548, 552, 556, 560, 564, 568, 572, 576, 580, 584, 588, 592, 596]
    norm = mpl.colors.BoundaryNorm(levels, 23)
    m.contourf(x,y,pvars['GHT'][time][lvl]/10,levels,cmap=colormap, norm=norm)


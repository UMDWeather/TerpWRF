import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndimage
from scipy.ndimage.filters import minimum_filter, maximum_filter
from mpl_toolkits.basemap import cm
import metpy.calc as mcalc
from metpy.units import units

filename='surfacedewpoint'
title ='2m Dew Point Temperature'
cbarlabel = 'Temperature (F)'
boundaryColor = 'gray'
frequency = 3                   # frequency in hrs


def plot(variables,prev_vars,pltenv):

    cont_int = 10
    cont_smooth = 0.5

    x = pltenv['x']
    y = pltenv['y']
    m = pltenv['map']

    bbox = dict(boxstyle="square",ec='None',fc=(1,1,1,0.75))

    #var = (variables['T2'][0]-273.15) * 1.8 + 32
    var = variables['Q2'][0]*1000.
    varp = variables['AFWA_MSLP'][0]*0.01
    var = var * units('g/kg')
    vare = mcalc.vapor_pressure(varp * units.mbar, var)
    vartd = mcalc.dewpoint(vare)
    vartd = vartd.to('degF')
    var2 = ndimage.gaussian_filter(vartd,sigma=cont_smooth)
    levels = np.arange(-100,150,cont_int)
    levels2 = np.arange(-40,140,1)

    P = m.contour(x,y,var2,levels=levels,colors='k')
    plt.clabel(P,inline=1,fontsize=10,fmt='%1.0f',inline_spacing=1)

    P = m.contour(x,y,var2,levels=[32],colors='r')
    plt.clabel(P,inline=1,fontsize=10,fmt='%1.0f',inline_spacing=1)

    m.contourf(x,y,vartd,cmap='gist_ncar', levels=levels2, extend='both')
#     #plot thickness
#     colors = [
#         (0, 540, 'cyan'),
#         (540, 541, 'blue'),
#         (546, 570, 'red'),
#         (570, 700, 'brown'),
#         ]

#     for c in colors:
#         levels = np.arange(c[0],c[1],6)
#         P = m.contour(x,y,thck2,levels=levels,colors=c[2], linestyles='dashed')
#         plt.clabel(P,inline=1,fontsize=10,fmt='%1.0f',inline_spacing=2)


#     # precip
#     precip = (variables['RAINNC'][time]+variables['RAINC'][time])*0.03937
#     if time >= frequency:
#         precip -= (variables['RAINNC'][time-3]+variables['RAINC'][time-3])*0.03937
        

#     nws_precip_colors = [
#         "#7fff00",  # 0.01 - 0.10 inches
#         "#00cd00",  # 0.10 - 0.25 inches
#         "#008b00",  # 0.25 - 0.50 inches
#         "#104e8b",  # 0.50 - 0.75 inches
#         "#1e90ff",  # 0.75 - 1.00 inches
#         "#00b2ee",  # 1.00 - 1.25 inches
#         "#00eeee",  # 1.25 - 1.50 inches

#         "#8968cd",  # 1.50 - 1.75
#         "#912cee",  # 1.75 -
#         "#8b008b",  # 2.0 - 
#         "#8b0000",  # 2.5 - 
#         "#cd0000",  # 3.0 -
#         "#ee4000",  # 4.0 -
#         "#ff7f00",  # 5.0 -
#         "#cd8500",  # 6.0 -
#         "#ffd700",  # 7.0 -
#         "#eeee00",  # 8.0 - 
#         "#ffff00",  # 9.0 -
#         ]
#     precip_colormap = mpl.colors.ListedColormap(nws_precip_colors)
#     levels = [0.01, 0.1, 0.25, 0.50, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0,
#           6.0, 7.0, 8.0, 9.0, 10.,]
#     norm = mpl.colors.BoundaryNorm(levels, 18)
    
#     m.contourf(x,y,precip,levels,cmap=precip_colormap, norm=norm)
# #    plt.colorbar()

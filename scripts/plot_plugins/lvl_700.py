import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndimage
from scipy.ndimage.filters import minimum_filter, maximum_filter
from mpl_toolkits.basemap import cm

filename='lvl_700'
title ='700mb Heights and Relative Humidity'
cbarlabel = 'Relative Humidity (%)'
boundaryColor = 'gray'
frequency = 3                   # frequency in hrs

def plot(variables,prev_vars,pltenv):

    cont_int = 10
    cont_smooth = 0.5
    thin = 10
    lvl = 3
    time = 0

    x = pltenv['x']
    y = pltenv['y']
    m = pltenv['map']


#    u = pvars['UU'][time][lvl] * 1.94384
#    v = pvars['VV'][time][lvl] * 1.94384
#    mag = np.sqrt(u**2 + v**2)
#    m.barbs(x[::thin,::thin], y[::thin,::thin], u[::thin,::thin], v[::thin,::thin], length=6)


    # bbox = dict(boxstyle="square",ec='None',fc=(1,1,1,0.75))

    var = variables['GHT_PL'][time][lvl]/10
    levels = np.arange(0,400,4)
    P = m.contour(x,y,var,levels=levels,colors='k')
    plt.clabel(P,inline=1,fontsize=10,fmt='%1.0f',inline_spacing=1)

    # plt.clabel(P,inline=1,fontsize=10,fmt='%1.0f',inline_spacing=1)


    # m.contourf(x,y,var, levels=levels2, extend='both')

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
        

    colors = [
        "#786103",
        "#967a16",
        "#b9992a",
        "#d2b450",
        "#e2d96e",
        "#e6e6b4",
        "#b1d499",
        "#41bf0a",
        "#329108",
        "#256406",
        "#134600",
        "#0c2c00",
        ]
    colormap = mpl.colors.ListedColormap(colors)
    levels = [0,10,20,30,40,50,60,70,80,90,95,100,105]
    norm = mpl.colors.BoundaryNorm(levels, 12)
    
    m.contourf(x,y,variables['RH_PL'][time][lvl],levels,cmap=colormap, norm=norm)
# #    plt.colorbar()

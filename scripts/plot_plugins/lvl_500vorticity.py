
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndimage
from scipy.ndimage.filters import minimum_filter, maximum_filter
from mpl_toolkits.basemap import cm

filename='lvl_500vorticity'
title ='500mb Relative Vorticity'
cbarlabel = 'X 10^-5 s^-1'
boundaryColor = 'gray'
frequency = 3                   # frequency in hrs

def plot(variables,prev_vars,pltenv):

    cont_int = 10
    cont_smooth = 0.5
    thin = 10
    lvl = 5 
    time = 0

    x = pltenv['x']
    y = pltenv['y']
    m = pltenv['map']

    var = variables['GHT_PL'][time][lvl]/10
    levels = np.arange(0,600,4)
    P = m.contour(x,y,var,levels=levels,colors='k')
    plt.clabel(P,inline=1,fontsize=10,fmt='%1.0f',inline_spacing=1)

    u = variables['U_PL'][time][lvl]
    v = variables['V_PL'][time][lvl]
 
    u.shape = v.shape

    #dX = 16000
    #dY = dX
    dX = pltenv['dX']
    dY = pltenv['dY']    

    dV = (np.gradient(v))
    Vgradient = dV[-1]/dX

    dU = (np.gradient(u))
    Ugradient = dU[-2]/dY

    RelVort = Vgradient - Ugradient

    lat = variables['XLAT']
    F = np.sin(lat)

    AbsoluteVort = RelVort + F
    NormalizedRelVort = RelVort * 100000

    colortable = [
		 "#ffffff",
                 "#ffff00",
		 "#ffee00",
		 "#ffdd00",
  		 "#ffcc00",
                 "#ffbb00",
		 "#ffaa00",
 		 "#ff9900",
		 "#ff8800",
	 	 "#ff7700",
	         "#ff6600",
		 "#ff5500",
		 "#ff4400",
		 "#ff3300",
		 "#ff2200",
		 "#ff1100",
		 "#ff0000",
		 ]
    vort_colormap = mpl.colors.ListedColormap(colortable)
    levels2 = np.arange(0,51,3)
    norm = mpl.colors.BoundaryNorm(levels2,19)
    m.contourf(x,y,NormalizedRelVort,levels=levels2,cmap=vort_colormap,norm=norm, extend='both')
  

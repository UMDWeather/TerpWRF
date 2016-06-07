import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndimage
from scipy.ndimage.filters import minimum_filter, maximum_filter
from mpl_toolkits.basemap import cm

filename='irsat'
title ='Simulated IR Satellite'
cbarlabel = 'Cloud Temperature (C)'
boundaryColor = 'gray'
frequency = 3                   # frequency in hrs

def plot(variables, pvars, pltenv, time):
    
    cont_int = 10
    cont_smooth = 0.5

    x = pltenv['x']
    y = pltenv['y']
    m = pltenv['map']
  
    olr = variables['OLR'][time]

    sbc = .000000056704	
    ir_T = ((olr / sbc) ** (0.25)) - 273
    
    colors = [
       "#000000",
       "#330033",
       "#660066",
       "#b300b3",
       "#b30000",
       "#cc0000",
       "#cc3300",
       "#cc6600",
       "#cc9900",
       "#ffcc00",
       "#99cc00",
       "#66cc00",
       "#33cc00",
       "#00cc00",
       "#00cc66",
       "#00cc99",
       "#00cccc",
       "#00e6e6",
       "#00ffff",
       "#99ffff",
       "#404040",
       "#4d4d4d",
       "#595959",
       "#666666",
       "#737373",
       "#808080",
       "#8c8c8c",
       "#999999",
       "#a6a6a6",
       "#bfbfbf",
       "#cccccc",
       "#d9d9d9",
       "#e6e6e6",
       ]
   
   
    colormap = mpl.colors.ListedColormap(colors)
  
    levels = [-85,-80,-78,-75,-72,-69,-66,-63,-60,-57,-54,-51,-48,-45,-42,-39,-36,-33,-30,-27,-24,-21,-18,-15,-12,-9,-6,-3,0,3,10]
    norm = mpl.colors.BoundaryNorm(levels, 33) 

    m.contourf(x,y,ir_T,levels,cmap=colormap, norm=norm, extend='both')

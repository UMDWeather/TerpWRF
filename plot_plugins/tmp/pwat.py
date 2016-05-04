import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndimage
from scipy.ndimage.filters import minimum_filter, maximum_filter
from mpl_toolkits.basemap import cm

filename='pwat'
title ='Total Precipitable Water (Inches)'
boundaryColor = 'gray'
frequency = 3                   # frequency in hrs


def plot(variables, pvars, pltenv, time):


    x = pltenv['x']
    y = pltenv['y']
    m = pltenv['map']


    g= 9.81
    P  = variables['P'][time]
    PB  = variables['PB'][time]
    Qv = variables['QVAPOR']

    Pr = PB +P
    np.shape(Pr)

    Qvap = Qv[time,:,:,:]
    np.shape(Qv) 

    # Now go through each point
    for j in range(len(Pr[0])):
		currow_pwat = []
		for i in range(len(Pr[0,0])):
			curcol_pwat = []		
			for k in range(len(Pr)-1):
				curdp = (Pr[k,j,i] - Pr[k+1,j,i]) * 0.01
				curpwat = curdp * Qv[k,j,i]
				curcol_pwat.append(curpwat)		
			np_curcol_pwat = np.array(curcol_pwat)
			point_pwat = np.sum(curcol_pwat)
			currow_pwat.append(point_pwat)		
		
		np_currow_pwat = np.array(currow_pwat)	
		if j == 0:
			total_pwat = np_currow_pwat
		else:
			total_pwat = np.row_stack((np_currow_pwat, total_pwat))


    pwat = np.divide(total_pwat,g)

    pwat_color = [
	"#674d32",
	"#734d26",
	"#7e4d1b",
	"#8a4d0f",
	"#954d04",
	"#b3b3e6",
	"#8c8cd9",
	"#6666cc",
	"#4040bf",
	"#333399",
	"#79d2a6",
	"#53c68c",
	"#39ac73",
	"#2d8659",
	"#00b359",
	"#40ff00",
	"#99ff33",
	"#ccff33",
	"#e6e600",
	"#ffff00",
	"#e6e600",
	"#ccffff",
	"#66ffff",
	"#00cccc",
	"#00b3b3",
	"#008080",
	]

    pwat_colormap = mpl.colors.ListedColormap(pwat_color)
    levels = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6]
    norm = mpl.colors.BoundaryNorm(levels, 27)

    m.contourf(x,y,pwat,levels,cmap=pwat_colormap, norm=norm, extend='both')

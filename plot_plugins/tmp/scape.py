import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndimage
from scipy.ndimage.filters import minimum_filter, maximum_filter
from mpl_toolkits.basemap import cm

filename='sbcape'
title ='Surface Based CAPE (J/kg)'
boundaryColor = 'gray'
frequency = 3                   # frequency in hrs  


def plot(variables, pvars, pltenv, time):


    cont_int = 10
    cont_smooth = 0.5

    x = pltenv['x']
    y = pltenv['y']
    m = pltenv['map']

    T = variables['T'][time]
    P = variables['P'][time]
    PB = variables['PB'][time]
    Qv = variables['QVAPOR'][time]

    PR = P + PB
    W = Qv/(1-Qv)
    TH = np.add(T,290.)
    T_K = np.multiply(TH, np.power(np.divide(PR,1000.),(287.04/1004.)))
    PR_h = PR / 100.
   
    np.shape(PR)
    np.shape(W)
    np.shape(T_K)

#    for j in range(len(T_K[1,:,1])):
#		curcol_c = []
#		for i in range(len(T_K[1,1,:])):
#				sparms = severe.CAPESOUND(PR_h[:,j,i],T_K[:,j,i],W[:,j,i])
#				curcol_c.append(sparms[1])		
#		np_curcol_c = np.array(curcol_c)
#		if j == 0:
#			cape = np_curcol_c
#		else:
#			cape = np.row_stack((cape, np_curcol_c))
 #
  #  np.shape(cape)
   
   # levels = np.arange(250,7000,250)

    #P = m.contour(x,y,cape,levels=levels,colors='k')
#    plt.clabel(P,inline=1,fontsize=10,fmt='%1.0f',inline_spacing=1)

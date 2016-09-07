import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndimage
from scipy.ndimage.filters import minimum_filter, maximum_filter
from mpl_toolkits.basemap import cm


filename='compositereflect'
title ='Simulated Composite Radar Reflectivity'
cbarlabel = 'dBZ'
boundaryColor = 'gray'
frequency = 3                   # frequency in hrs

def extrema(mat,mode='wrap',window=10):
    """find the indices of local extrema (min and max)
    in the input array."""
    mn = minimum_filter(mat, size=window, mode=mode)
    mx = maximum_filter(mat, size=window, mode=mode)
    # (mat == mx) true if pixel is equal to the local max
    # (mat == mn) true if pixel is equal to the local in
    # Return the indices of the maxima, minima
    return np.nonzero(mat == mn), np.nonzero(mat == mx)


def plot(variables,prev_vars,pltenv):

    gauss_sigma = 3
    time = 0

    cont_int = 10
    cont_smooth = 0.5

    x = pltenv['x']
    y = pltenv['y']
    m = pltenv['map']


    bbox = dict(boxstyle="square",ec='None',fc=(1,1,1,0.75))

    #calculate MSLP with smoothing
    mtemp = variables['T2'][time] + 6.5*variables['HGT'][time]/1000./2.
    mslp = variables['PSFC'][time] * np.exp(9.81/(287.0*mtemp)*variables['HGT'][time])*0.01
    #mslp = variables['AFWA_MSLP'][time]
    mslp2 = ndimage.gaussian_filter(mslp,sigma=gauss_sigma)
    levels = np.arange(0,1500,4)
    P=m.contour(x,y,mslp2, levels=levels,colors='k')
    plt.clabel(P,inline=1,fontsize=10,fmt='%1.0f',inline_spacing=1)


    #plot lows and high
    mslp3 = ndimage.gaussian_filter(mslp,sigma=7)
    local_min, local_max = extrema(mslp3, window=5)
    xlows = x[local_min]; xhighs = x[local_max]
    ylows = y[local_min]; yhighs = y[local_max]
    lowvals = mslp[local_min]; highvals = mslp[local_max]

    # plot lows as blue L's, with min pressure value underneath.
    xyplotted = []
    # don't plot if there is already a L or H within dmin meters.
    yoffset = 0.022*(m.ymax-m.ymin)
    dmin = yoffset
    for hlx,hly,p in zip(xlows, ylows, lowvals):
        if hlx < m.xmax and hlx > m.xmin and hly < m.ymax and hly > m.ymin:
            dist = [np.sqrt((hlx-x0)**2+(hly-y0)**2) for x0,y0 in xyplotted]
            if not dist or min(dist) > dmin:
                plt.text(hlx,hly,'L',fontsize=16,fontweight='bold',
                    ha='center',va='center',color='r')
                plt.text(hlx,hly-yoffset,repr(int(p)),fontsize=11,
                    ha='center',va='top',color='r',
                    bbox = bbox)
                xyplotted.append((hlx,hly))

    # plot highs as red H's, with max pressure value underneath.
    xyplotted = []
    for hlx,hly,p in zip(xhighs, yhighs, highvals):
        if hlx < m.xmax and hlx > m.xmin and hly < m.ymax and hly > m.ymin:
            dist = [np.sqrt((hlx-x0)**2+(hly-y0)**2) for x0,y0 in xyplotted]
            if not dist or min(dist) > dmin:
                plt.text(hlx,hly,'H',fontsize=16,fontweight='bold',
                    ha='center',va='center',color='b')
                plt.text(hlx,hly-yoffset,repr(int(p)),fontsize=11,
                    ha='center',va='top',color='b',
                    bbox = bbox)
                xyplotted.append((hlx,hly))

    QR = variables['QRAIN']
    try:
        QS = variables['QSNOW']
    except:
        QS = np.zeros(np.shape(QR))


    # Define 'constant' densities (kg m-3)
    rhor = 1000
    rhos = 100
    rhog = 400
    rhoi = 917


    # Define "fixed intercepts" (m-4)
    Norain = 8.0E6
    #Nosnow = 2.0E7
    Nosnow = 2.0E6*np.exp(-0.12 * (variables['T2'][time]-273))
    Nograu = 4.0E6


    # First, find the density at the first sigma level
    # above the surface
    density = np.divide(variables['PSFC'][time],(287.0 * variables['T2'][time]))
    
    Qra_all = QR[time]
    Qsn_all = QS[time]

    for j in range(len(Qra_all[1,:,1])):
                curcol_r = []
                curcol_s = []
                for i in range(len(Qra_all[1,1,:])):
                                maxrval = np.max(Qra_all[:,j,i])
                                maxsval = np.max(Qsn_all[:,j,i])
                                curcol_r.append(maxrval)
                                curcol_s.append(maxsval)
                np_curcol_r = np.array(curcol_r)
                np_curcol_s = np.array(curcol_s)
                if j == 0:
                        Qra = np_curcol_r
                        Qsn = np_curcol_s
                else:
                        Qra = np.row_stack((Qra, np_curcol_r))
                        Qsn = np.row_stack((Qsn, np_curcol_s))
    # Calculate slope factor lambda
    lambr = np.divide((3.14159 * Norain * rhor), np.multiply(density, Qra))
    lambr = lambr ** 0.25

    #lambs = np.divide((3.14159 * Nosnow * rhoi), np.multiply(density, Qsn))
    #lambs = lambs ** 0.25
    lambs = np.exp(-0.0536 * (variables['T2'][time]- 273))

    # Calculate equivalent reflectivity factor
    Zer = (720.0 * Norain * (lambr ** -7.0)) * 1E18
    Zes = (0.224 * 720.0 * Nosnow * (lambr ** -7.0) * (rhos/rhoi) ** 2) * 1E18
    Zes_int = np.divide((lambs * Qsn * density), Nosnow)
    Zes = ((0.224 * 720 * 1E18) / (3.14159 * rhor) ** 2) * Zes_int ** 2



    Ze = np.add(Zer, Zes)
    #Ze = Zer
    # Convert to dBZ
    dBZ = 10 * np.log10(Ze)
    dBZ = np.nan_to_num(dBZ)

    radarcolors = [
        "#ffffff",
        "#00ffff",
        "#0099ff",
        "#0000ff",
        "#00ff00",
        "#00cc00",
        "#009900",
        "#ffff00",
        "#cccc00",
        "#ff9900",
        "#ff0000",
        "#d40000",
        "#bc0000",
        "#ff00ff",
        "#9966cc",
        "#ffffff"
        ]


    colormap = mpl.colors.ListedColormap(radarcolors)
    levels = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75]
    norm = mpl.colors.BoundaryNorm(levels, 16)

    m.contourf(x,y, dBZ, levels,cmap=colormap,norm=norm,extend="both",alpha=0.7)


                                                                         



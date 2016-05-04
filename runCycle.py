#!/bin/env python
#----------------------------------------------------------------------------------------
# runCycle.py
# Runs a wrf forecast using the most recent GFS boundary conditions.
#----------------------------------------------------------------------------------------
import logging


logLevel = logging.INFO
tmpDir = '/home/wrf/tmp'
fcstLength = 36        #forecast length in hours
maxCores = 36
abort_on_exist = False

#-------------------------------------
#-------------------------------------
#-------------------------------------


#setup logging
log = logging.getLogger(__name__)
log.setLevel(logLevel)

import datetime
import os
import sys
import shutil
import subprocess
import time
import wrf

def run():
    '''Runs the WRF using the most recent boundary conditions
    returns the date of the initial conditions, or False
    if it is determined the model has already run for the given initial condition date'''
    global tmpDir
    global fcstLength
    global maxCores
    global abort_on_exist

    #what is our starting/ending date
    startdate=wrf.bdyAvail()[-1]
    enddate = startdate+datetime.timedelta(hours=fcstLength)

    #create the temproary directory
    # and link in the required WRF files
    tmpDir = tmpDir+startdate.strftime('/wrf_%Y%m%d%H')
    if os.path.exists(tmpDir):
        if abort_on_exist:
            log.info('{0} has already been run, aborting job'.format(tmpDir))
            return False

        clearDelay=10 #time to wait, in seconds, before clearing tmp directory, gives user
                     #a chance to abort
        log.warn('Temporary directory {0} already exists... deleting in {1} seconds...'.format(tmpDir,clearDelay))
        time.sleep(clearDelay)
        log.warn('Clearing old temporary directory')
        shutil.rmtree(tmpDir)    
    else:
        log.info('using temporary directory {0}'.format(tmpDir))
    os.makedirs(tmpDir)
    wrf.lnkWPS(tmpDir)
    wrf.lnkWRF(tmpDir)
    wrf.lnkTools(tmpDir)

    #create the wrf/wps namelist files
    wrf.writeNamelists(tmpDir, startdate, enddate)

    #geogrid.exe
    log.info('Running geogrid...')
    sp=subprocess.Popen(tmpDir+'/geogrid.exe > geogrid.out 2> geogrid.err',cwd=tmpDir,shell=True)
    sp.wait()
    log.info('Geogrid run complete')

    #Get the GFS boundary conditions
    wrf.getBdy(startdate, tmpDir, length=fcstLength)

    #create the boundary / initial conditions for WRF
    log.info('running link_grib.csh...')
    sp=subprocess.Popen([tmpDir+'/link_grib.csh','gfs.t*'],cwd=tmpDir)
    sp.wait()

    log.info('Running ungrib.exe ...')
    sp=subprocess.Popen('./ungrib.exe > ungrib.out 2> ungrib.err',cwd=tmpDir, shell=True)
    sp.wait()
    log.info('Ungrib run complete')

    log.info('Running metgrid.exe ...')
    sp=subprocess.Popen('./metgrid.exe > metgrid.out 2> metgrid.err',cwd=tmpDir, shell=True)
    sp.wait()
    log.info('Metgrid run complete')

    log.info('Running real.exe ...')
    sp=subprocess.Popen('./real.exe > real.out 2> real.err',cwd=tmpDir, shell=True)
    sp.wait()
    log.info('Real run complete')

    #run WRF
    log.info('Running WRF.exe ...')
    sp=subprocess.Popen('mpirun -n 36 ./wrf.exe > wrf.out 2> wrf.err',cwd=tmpDir, shell=True)
    sp.wait()
    log.info('WRF run complete')

    #post process onto pressure levels
    log.info('Post processing WRF output...')
    sp=subprocess.Popen('cp -f ./namelist.vinterp1 namelist.vinterp',cwd=tmpDir, shell=True)
    sp.wait()
    sp=subprocess.Popen('./WRF_interp > wrf_interp.out 2> wrf_interp.err',cwd=tmpDir, shell=True)
    sp.wait()
    sp=subprocess.Popen('cp -f ./namelist.vinterp2 namelist.vinterp',cwd=tmpDir, shell=True)
    sp.wait()
    sp=subprocess.Popen('./WRF_interp > wrf_interp.out 2> wrf_interp.err',cwd=tmpDir, shell=True)
    sp.wait()
    log.info('wrf_interp complete')
    
    return startdate



if (__name__ == '__main__'):
    logging.addLevelName( logging.WARNING, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
    logging.addLevelName( logging.DEBUG, "\033[1;32m%s\033[1;0m" % logging.getLevelName(logging.DEBUG))
    logging.addLevelName( logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('[%(asctime)s %(levelname)s] %(name)s: %(message)s'))
    log.addHandler(ch)
    ch.setLevel(logging.DEBUG)

    log.info('-----------------------------------------------------------------')
    log.info('runCycle.py - realtime WRF run script wrapper. Travis Sluka. 2014')
    log.info('-----------------------------------------------------------------')
    run()

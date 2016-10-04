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

from contextlib import contextmanager
import datetime
import os
import sys
import shutil
import subprocess
import time
import wrf
import wrfdb
import signal

@contextmanager
def timeout(seconds):
    def timeout_handler(signum, frame):
        pass
    original_handler = signal.signal(signal.SIGALRM, timeout_handler)
    try:
        signal.alarm(seconds)
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_handler)

def run():
    '''Runs the WRF using the most recent boundary conditions
    returns the date of the initial conditions, or False
    if it is determined the model has already run for the given initial condition date'''
    global tmpDir
    global fcstLength
    global maxCores
    global abort_on_exist

    #what is our starting/ending date
    with timeout(60):
      try:
        startdate=wrf.bdyAvail()[-1]
      except:
	log.info('Timeout...')
	return False	
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
    # send message to database that model is starting
    wrfdb.status('TerpWRF is starting soon...',1,startdate.strftime("%HZ"))
    os.makedirs(tmpDir)
    wrf.lnkWPS(tmpDir)
    wrf.lnkWRF(tmpDir)

    #create the wrf/wps namelist files
    wrf.writeNamelists(tmpDir, startdate, enddate)
    # copy IO options
    wrf.writeIOcontrol(tmpDir)

    #geogrid.exe
    log.info('Running geogrid...')
    wrfdb.status('Running geogrid...',2,startdate.strftime("%HZ"))
    sp=subprocess.Popen(tmpDir+'/geogrid.exe > geogrid.out 2> geogrid.err',cwd=tmpDir,shell=True)
    sp.wait()
    log.info('Geogrid run complete')

    #Get the GFS boundary conditions
    wrfdb.status('Downloading GFS boundary conditions...',3,startdate.strftime("%HZ"))
    wrf.getBdy(startdate, tmpDir, length=fcstLength)

    #create the boundary / initial conditions for WRF
    log.info('running link_grib.csh...')
    sp=subprocess.Popen([tmpDir+'/link_grib.csh','gfs.t*'],cwd=tmpDir)
    sp.wait()
    

    wrfdb.status('Extracting vars from GFS GRIB files...',4,startdate.strftime("%HZ"))
    log.info('Running ungrib.exe ...')
    sp=subprocess.Popen('./ungrib.exe > ungrib.out 2> ungrib.err',cwd=tmpDir, shell=True)
    sp.wait()
    log.info('Ungrib run complete')

    wrfdb.status('Preprocessing meteorological input...',5,startdate.strftime("%HZ"))
    log.info('Running metgrid.exe ...')
    sp=subprocess.Popen('./metgrid.exe > metgrid.out 2> metgrid.err',cwd=tmpDir, shell=True)
    sp.wait()
    log.info('Metgrid run complete')

    wrfdb.status('Initializing WRF model...',6,startdate.strftime("%HZ"))
    log.info('Running real.exe ...')
    sp=subprocess.Popen('./real.exe > real.out 2> real.err',cwd=tmpDir, shell=True)
    sp.wait()
    log.info('Real run complete')

    # initialize Plotbot
    sp1 = subprocess.Popen('./TerpWRF-plotbot '+tmpDir,cwd='/home/wrf/TerpWRF/scripts/', shell=True)

    #run WRF
    wrfdb.status('TerpWRF is running...',7,startdate.strftime("%HZ"))
    log.info('Running WRF.exe ...')
    sp=subprocess.Popen('mpirun -n 36 ./wrf.exe > wrf.out 2> wrf.err',cwd=tmpDir, shell=True)
    sp.wait()
    log.info('WRF run complete')
    time.sleep(120)
    sp1.kill() # kill plotbot
    
    wrfdb.status('Misc. products being generated',8,startdate.strftime("%HZ"))
    # create text output and meteograms
    log.info('Creating meteograms and text output...')
    sp = subprocess.Popen('python /home/wrf/TerpWRF/scripts/TerpWRF-stations',cwd=tmpDir, shell=True)
    sp.wait() 
    
    # create soundings
    log.info('Creating simulated soundings...')
    sp = subprocess.Popen('python /home/wrf/TerpWRF/scripts/TerpWRF-soundings',cwd=tmpDir, shell=True)
    sp.wait() 

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

#!/usr/bin/env python
#------------------------------------------------------
# cronjob.py
# Main cronjob script for running operational WRF runs.
# Checks for the most recent GFS output, download it and uses it
# as boundary conditions. After running a WRF forecast, generates
# output plots, and sets as the newest WRF output directory. Cleans up
# any old WRF runs beyond a certain age
#------------------------------------------------------

from contextlib import contextmanager
import signal,errno
import time
import fcntl
import sys
from glob import glob
import os
import shutil
import datetime as dt

import wrf
import runCycle

import subprocess

#-------------------------------------------------------
#-------------------------------------------------------
# configurable parameters

tmpDir = '/home/wrf/tmp'
outputDir = '/var/www/html/wrf/output'
runCycle.maxCores = 36 
runCycle.fcstLength = 120 
runCycle.tmpDir = tmpDir
lock_filename = tmpDir + '/wrfCron.lck'
maxOutput = 7 #max number of days of output to keep

debug = False

#-------------------------------------------------------
#-------------------------------------------------------
begintime = time.time()


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


#get a file lock, make sure no one else is running the wrf script
lck_file=open(lock_filename,'w')
locked = False
with timeout(2):
    try:
        fcntl.flock(lck_file.fileno(),fcntl.LOCK_EX)
        locked = True
    except IOError, e:
        if e.errno != errno.EINTR:
            raise e
        #lock timeout

#unable to get lock? wrf must already be running, abandon script
if not locked:
    print "can't get lock"
    sys.exit(0)



#---------------------------------
#otherwise, start doing stuff
#---------------------------------
import logging
import logging.handlers

logLevel = logging.INFO
logFile = tmpDir+'/wrfCron.log'

#setup logging in a rotating output file
logging.addLevelName( logging.WARNING, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
logging.addLevelName( logging.DEBUG, "\033[1;32m%s\033[1;0m" % logging.getLevelName(logging.DEBUG))
logging.addLevelName( logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
log = logging.getLogger()
if debug:
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
else:
    log.setLevel(logging.INFO)
    ch = logging.handlers.RotatingFileHandler(logFile, maxBytes=1024*1024*5, backupCount=5)
ch.setFormatter(logging.Formatter('[%(asctime)s %(levelname)s] %(name)s: %(message)s', datefmt='%Y-%m-%d,%H:%M:%S'))
log.addHandler(ch)

#-------------------------------------
# run a forecast
log.info('--------------------------------------------------------------------')
runCycle.abort_on_exist = True

startdate = runCycle.run()

#if forecast run was successful
if startdate:
    # move the output
    wrffiles = glob(tmpDir+startdate.strftime("/wrf_%Y%m%d%H/wrfout*"))
    wrkDir=outputDir+startdate.strftime("/%Y%m%d%H")
    os.makedirs(wrkDir)
    for f in wrffiles:
        shutil.copyfile(f, wrkDir+'/'+f.split('/')[-1])

    # generate plots
    sp=subprocess.Popen('python plot.py l '+wrkDir,cwd='/home/wrf/scripts', shell=True)    
    sp=subprocess.Popen('python plot.py h '+wrkDir,cwd='/home/wrf/scripts', shell=True)    
    # generate meteograms
    sp=subprocess.Popen('python meteogram.py h '+wrkDir+' /home/wrf/scripts/stations.toplot.highres',cwd='/home/wrf/scripts',shell=True)
    sp=subprocess.Popen('python meteogram.py l '+wrkDir+' /home/wrf/scripts/stations.toplot.lowres',cwd='/home/wrf/scripts',shell=True)
    # generate soundings
    sp=subprocess.Popen('python sounding.py h '+wrkDir+' /home/wrf/scripts/stations.toplot.highres',cwd='/home/wrf/scripts',shell=True)
    sp=subprocess.Popen('python sounding.py l '+wrkDir+' /home/wrf/scripts/stations.toplot.lowres',cwd='/home/wrf/scripts',shell=True)

    # cleanup old tmp directories and model output.
    #  leave only the previous day of runs in the /var/tmp directory
    log.info('Cleaning up old tmp and previous runs...')
    dirs = sorted(glob(tmpDir+'/wrf_??????????'))[:-4]
    for d in dirs:
        log.info(' Removing {0}'.format(d))
        shutil.rmtree(d)
    # email when completed
    duration = time.time() - begintime
    #log.info('php sendmail.php '+startdate.strftime('%H')+' '+str(duration/60.))
    sp=subprocess.Popen('php sendmail.php '+startdate.strftime('%H')+' '+str(duration/60.),cwd='/home/wrf/scripts',shell=True)

log.debug('Removing old runs')
dirs = sorted(glob(outputDir+'/??????????'))
cutoff = (dt.datetime.utcnow()-dt.timedelta(days=maxOutput)).strftime('%Y%m%d%H')
for d in dirs:
    if (d.split('/')[-1] < cutoff):
	try:
	    log.info('deleting {0}'.format(d))
	    shutil.rmtree(d)
	except Exception, e:
	    log.error('Unable to delete directory tree: '+str(e))


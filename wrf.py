#!/usr/bin/env python
import datetime as dt
import logging
import re
import ftplib
import os
import time

log = logging.getLogger(__name__)


www_ncep='ftp.ncep.noaa.gov'
www_gfs='/pub/data/nccf/com/gfs/prod'

defaultVersion='WRF3.7.1'
configFiles=os.path.realpath('./config')


#------------------------------------------------------------------------------------------------
def bdyAvail(model='GFS'):
    """Return list of date/times of recent model runs available.
    Default model used is the GFS. 
    """
    log = getFnLog()
    log.info('Getting list of {0} boundary conditions from {1}'.format(model,www_ncep))

    #log into the ftp and get the directory list
    ftp = ftplib.FTP(www_ncep)
    ftp.login('anonymous','')
    ftp.cwd(www_gfs)
    dirs=sorted(ftp.nlst())

    #hardcoded to search only for GFS, change this eventually
    #get a list of all currently available dates
    dates = []
    for d in dirs:
        if re.match('^gfs\..*$',d):
            #check to make sure that the folder contains all the dates, every 3
            # hours up to 192 hr
            ftp.cwd(www_gfs+'/'+d)
            sdirs=sorted(ftp.nlst())

            matches=[]
            for sd in sdirs:
                if re.match('^gfs\.t..z\.pgrb2.0p25.f[0-9]+$',sd):
                    matches.append(sd)
		
            #if len(matches) >= 65:
            #    matches=sorted(matches)
            #    if matches[64][-3:]=='192' :
            #        dates.append(dt.datetime.strptime(d,'gfs.%Y%m%d%H'))
	    if len(matches) >= 121:
		 matches=sorted(matches)
		 if matches[120][-3:]=='120' :
		     dates.append(dt.datetime.strptime(d,'gfs.%Y%m%d%H'))

    ftp.quit()
    log.debug('{0} {1} output dates found online at {2}'.format(len(dates),model,www_ncep+www_gfs))
    log.debug('GFS dates range from {0} to {1} (most recent)'.format(str(dates[0]),str(dates[-1])))
    print('GFS dates range from {0} to {1} (most recent)'.format(str(dates[0]),str(dates[-1])))
    return dates


def dload(dfile,urldest):
	import urllib
	print('Downloading '+dfile)
	urllib.urlretrieve(dfile,urldest)

#------------------------------------------------------------------------------------------------
def getBdy(date, dest, length='All', model='GFS'):
    """Gets the boundary conditions for <date> and places it in 
    the directory <dest>
    """
    log = getFnLog()
    import urllib
    import multiprocessing

    if length == 'All':
        length = 384
    else:
        if length < 0 or length > 384:
            log.warn('Invalid fcst length passed to getBdy ({0}), setting to 364'.format(length))
            length = 364

    log.info('Downloading {0} boundary conditions starting {1} for {2} hours'.format(model,str(date), length))
    filename_template=date.strftime('gfs.t%Hz.pgrb2.0p25.f{0:03}')


    for fcstHr in range(0,length+1,3):
        filename=filename_template.format(fcstHr)
	url = 'ftp://{0}{1}/{2}/{3}'.format(www_ncep,www_gfs,date.strftime('gfs.%Y%m%d%H'),filename)
	urldest = dest+'/'+filename
        log.info('Downloading {0} ...'.format(filename))
	exec('p'+str(fcstHr)+' = multiprocessing.Process(target=dload, args=(url,urldest))')

	exec('p'+str(fcstHr)+'.start()')
	time.sleep(1)
    exec('p'+str(fcstHr)+'.join()')
        #urllib.urlretrieve('ftp://{0}{1}/{2}/{3}'.format(www_ncep,www_gfs,date.strftime('gfs.%Y%m%d%H'),filename)
        #                   ,dest+'/'+filename)


#------------------------------------------------------------------------------------------------
def lnkWPS(dest, version=defaultVersion):
    '''Creates links to the required wrf WPS files in the <dest> directory'''
    log = getFnLog()
    
    log.info('Copying files (version={0}) into {1}'.format(version, dest))
    rootPath=os.path.realpath('../{0}/WPS/'.format(version))
    files=[
        'geogrid.exe',
        'link_grib.csh',
        'metgrid.exe',
        'ungrib.exe',]
    for f in files:
        filename=rootPath+'/'+f
        log.debug('copying {0} to {1}'.format(filename,dest))
        os.symlink(filename,dest+'/'+f)

    os.symlink(rootPath+'/ungrib/Variable_Tables/Vtable.GFS_new', dest+'/Vtable')

    log.info('Finished linking files')



#------------------------------------------------------------------------------------------------
def lnkWRF(dest, version=defaultVersion):
    '''Creates links to the required wrf WRF files in the <dest> directory'''
    log = getFnLog()
    from glob import glob
    
    log.info('Copying files (version={0}) into {1}'.format(version, dest))
    root=os.path.realpath('../{0}/WRFV3/run/'.format(version))    

    files=glob(root+'/*')

    for f in files:
        log.debug('copying {0} to {1}'.format(f,dest))
        os.symlink(f,dest+'/'+os.path.basename(f))

    log.info('Finished linking files')




#------------------------------------------------------------------------------------------------
def lnkTools(dest, version=defaultVersion):
    log = getFnLog()
    root=os.path.realpath('../tools')    
    
    
    files = [
        root+'/WRF_INTERP/WRF_interp',
        root+'/../scripts/config/namelist.vinterp1',
        root+'/../scripts/config/namelist.vinterp2',
						]
    for f in files:
        os.symlink(f,dest+'/'+os.path.basename(f))



#------------------------------------------------------------------------------------------------
def writeNamelists(dest,startdate,enddate):
    '''Reads in a template for the namelist.wps and namelist.input files,
    replacing {...} words with the values that we want for this run'''
    log=getFnLog()

   
    #-------------------------------------
    #Create namelist.wps
    infilename = configFiles+'/namelist.wps'
    log.info('creating namelist.wps from template in {0}'.format(infilename))
    
    infile = open(infilename)
    outfile = open(dest+'/namelist.wps', 'w')

    replacements = {
        '{startdate}':startdate.strftime('%Y-%m-%d_%H:%M:%S'),
        '{enddate}':enddate.strftime('%Y-%m-%d_%H:%M:%S')}
    for line in infile:
        for src, target in replacements.iteritems():
            line = line.replace(src,target)
        outfile.write(line)
    infile.close()
    outfile.close()
    
    #-------------------------------------
    #Create namelist.input
    infilename = configFiles+'/namelist.input'
    log.info('creating namelist.input from template in {0}'.format(infilename))
    
    infile = open(infilename)
    outfile = open(dest+'/namelist.input', 'w')

    replacements = {
        '{start_yr}':str(startdate.year),
        '{start_mn}':str(startdate.month),
        '{start_dy}':str(startdate.day),
        '{start_hh}':str(startdate.hour),
        '{start_mm}':str(startdate.minute),
        '{start_ss}':str(startdate.second),
        '{end_yr}':str(enddate.year),
        '{end_mn}':str(enddate.month),
        '{end_dy}':str(enddate.day),
        '{end_hh}':str(enddate.hour),
        '{end_mm}':str(enddate.minute),
        '{end_ss}':str(enddate.second),
        }
    for line in infile:
        for src, target in replacements.iteritems():
            line = line.replace(src,target)
        outfile.write(line)
    infile.close()
    outfile.close()


#------------------------------------------------------------------------------------------------
    



#------------------------------------------------------------------------------------------------
def getFnLog():   
    '''Get a logger named specifically for the function it was called from.'''
    import inspect
    return logging.getLogger(__name__+'.'+inspect.stack()[1][3]+'()')

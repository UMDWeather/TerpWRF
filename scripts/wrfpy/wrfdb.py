import MySQLdb as mdb 

# below for mysql wrf status database
dbuser = 'wrf'
dbpass = 'SkamarockNroll'
dbhost = 'localhost'
dbname = 'TerpWRF'
dbtable = 'Status'

def status(msg,code,run):
	'Insert into mySQL database table log of WRF activity'
	### database stuff now
	con = mdb.connect(dbhost,dbuser,dbpass,unix_socket='/var/lib/mysql/mysql.sock') # socket info for RHEL issue
	
	with con:
		cur = con.cursor()
		cur.execute("USE %s" %(dbname))
		cur.execute("INSERT INTO %s (Status,StatusCode,ModelRun) VALUES ('%s',%s,'%s')" % (dbtable,msg,code,run))

def last():
	'Get the most recent status message'
        ### database stuff now
        con = mdb.connect(dbhost,dbuser,dbpass,unix_socket='/var/lib/mysql/mysql.sock') # socket info for RHEL issue

        with con:
                cur = con.cursor()
                cur.execute("USE %s" %(dbname))
		cur.execute("SELECT * FROM %s ORDER BY Time desc limit 1" %(dbtable))
                row = cur.fetchone()
	return row

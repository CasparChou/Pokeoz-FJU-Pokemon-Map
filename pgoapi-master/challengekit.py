import MySQLdb
import urllib
import sys
from time import sleep

def db_connect():
    sys.stdout.write("MySQL Conntecting....")
    sys.stdout.flush()
    db = MySQLdb.connect("localhost","root","pokemon","pokemon")
    cursor = db.cursor()
    db.set_character_set('utf8')
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET time_zone = "+08:00";')
    cursor.execute('SET GLOBAL time_zone = "+8:00";')
    cursor.execute('SET character_set_connection=utf8;')
    print "..success!"
    return (db, cursor)

def db_commit( db, cursor, sql ):
    try:
        db.set_character_set('utf8')
        cursor.execute('SET NAMES utf8;')
        cursor.execute('SET time_zone = "+08:00";')
        cursor.execute('SET GLOBAL time_zone = "+8:00";')
        cursor.execute('SET character_set_connection=utf8;')
        cursor.execute(sql)
        db.commit()
        print " "
        print "Database Successful!"
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])


def requestNewChallenge(botid, time, url):
    remove = ("UPDATE challenge SET \
            token = 'expire' WHERE botid = '%s' AND token = ' '") % botid
    sql = "INSERT IGNORE INTO challenge VALUES (\
            '%s', '%s', '%s', ' ')" %( time, botid, url )

    db, cursor = db_connect()
    db_commit( db, cursor, remove )
    db_commit( db, cursor, sql )
    db.close()

def checkTokenUpdate(challengeid):
    wait()
    sql = "SELECT token FROM challenge \
        WHERE timestamp = '%s'"%( challengeid )
        
    db, cursor = db_connect()
    cursor.execute( sql )
    token = cursor.fetchone()
    db.close()
    return token

def wait(stop=10): 
    for i in range(stop):
        sys.stdout.write("----------- Slow down ! Act like a human ! in %d s    -----------------\r" % (stop-i) )
        sys.stdout.flush()
        sleep(1)
    

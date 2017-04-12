import sys
import MySQLdb
from math import radians, cos, sin, asin, sqrt
from time import sleep

def wait(stop=10):
    for i in range(stop):
        sys.stdout.write("----------- Slow down ! Act like a human ! in %d s   -----------------\r" % (stop-i) )
        sys.stdout.flush()
        sleep(1)

def distance(lat0, lng0, lat1, lng1):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lat0, lng0, lat1, lng1 = map(radians, [lat0, lng0, lat1, lng1])
    # haversine formula 
    dlng = lng1 - lng0 
    dlat = lat1 - lat0 
    a = sin(dlat/2)**2 + cos(lat0) * cos(lat1) * sin(dlng/2)**2
    c = 2 * asin(sqrt(a)) 
    m = 6367000 * c
    return m

def get_key_from_pokemon(pokemon):
    return '{}-{}'.format(pokemon['spawn_point_id'], pokemon['pokemon_data']['pokemon_id'])

def insert_data(poks):
    if( len(poks) == 0 ):
	return
    print ("[Found] There are " + str(len(poks)) + " pokemons around here !" )
    #log.info( "[Found] There are " + str(len(poks)) + " pokemons around here !" )
    db = MySQLdb.connect( "localhost", "root", PASSWORD_HAS_BEEN_REMOVED, DB_HAS_BEEN_REMOVED )
    cursor =  db.cursor()
    
    sql = "INSERT IGNORE INTO encounter \
        (encounter_id, spawn_point_id,\
        latitude,longitude,\
        pokemon_id, expire)  VALUES"
		
    for i, pod in enumerate( poks ):
        if i > 0 :
	    sql += ", "
	sql += "('%s', '%s', '%s', '%s', %d, %d)"%(\
		str(poks[pod]["encounter_id"]), \
		poks[pod]["spawn_point_id"], \
		poks[pod]["latitude"], \
		poks[pod]["longitude"], \
		int(poks[pod]["pokemon_data"]["pokemon_id"]), \
		long(poks[pod]["hides_at"]) )

    try:
        cursor.execute( sql )
        db.commit()
    except MySQLdb.Error, e:
        db.rollback()
        print sql
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    db.close()
    
def insert_spawn(poks):
    if( len(poks) == 0 ):
	return
    for p in poks:
        print poks[p]['id'] + "," + poks[p]['latitude']

    db = MySQLdb.connect( "localhost", "root", PASSWORD_HAS_BEEN_REMOVED, DB_STR_HAS_BEEN_REMOVED )
    cursor =  db.cursor()
    
    sql = "INSERT IGNORE INTO spawn_points VALUES"
		
    for i, pod in enumerate( poks ):
    	if i > 0 :
	        sql += ", "
    	sql += "('%s', '%s', '%s')"%(\
		    poks[pod]["id"], \
    		poks[pod]["latitude"], \
    		poks[pod]["longitude"] \
        )
    try:
        cursor.execute( sql )
     	db.commit()
    except MySQLdb.Error, e:
        db.rollback()
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        print sql
    db.close()


#!/usr/bin/env python
"""
pgoapi - Pokemon Go API
Copyright (c) 2016 tjado <https://github.com/tejado>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.:

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

Author: tjado <https://github.com/tejado>
"""

import os
import sys
import json
import time
import pprint
import logging
import getpass
import argparse
import json
import MySQLdb
from random import randint
from math import radians, cos, sin, asin, sqrt

# add directory of this file to PATH, so that the package will be found
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# import Pokemon Go API lib
from pgoapi import pgoapi
from pgoapi import utilities as util


log = logging.getLogger(__name__)

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

def init_config():
    parser = argparse.ArgumentParser()
    config_file = "config.json"

    # If config file exists, load variables from json
    load   = {}
    if os.path.isfile(config_file):
        with open(config_file) as data:
            load.update(json.load(data))

    # Read passed in Arguments
    required = lambda x: not x in load
    parser.add_argument("-a", "--auth_service", help="Auth Service ('ptc' or 'google')",
        required=required("auth_service"))
    parser.add_argument("-u", "--username", help="Username", required=required("username"))
    parser.add_argument("-p", "--password", help="Password")
    parser.add_argument("-l", "--location", help="Location", required=required("location"))
    parser.add_argument("-d", "--debug", help="Debug Mode", action='store_true')
    parser.add_argument("-t", "--test", help="Only parse the specified location", action='store_true')
    parser.add_argument("-px", "--proxy", help="Specify a socks5 proxy url")
    parser.set_defaults(DEBUG=False, TEST=False)
    config = parser.parse_args()

    # Passed in arguments shoud trump
    for key in config.__dict__:
        if key in load and config.__dict__[key] == None:
            config.__dict__[key] = str(load[key])

    if config.__dict__["password"] is None:
        log.info("Secure Password Input (if there is no password prompt, use --password <pw>):")
        config.__dict__["password"] = getpass.getpass()

    if config.auth_service not in ['ptc', 'google']:
      log.error("Invalid Auth service specified! ('ptc' or 'google')")
      return None

    return config

def get_key_from_pokemon(pokemon):
    return '{}-{}'.format(pokemon['spawn_point_id'], pokemon['pokemon_data']['pokemon_id'])

def wait(stop=10):
    for i in range(stop):
        sys.stdout.write("----------- Slow down ! Act like a human ! in %d s   -----------------\r" % (stop-i) )
        sys.stdout.flush()
        time.sleep(1)

def walkTo(api, olatitude, olongitude, epsilon=10, step=7.5, delay=10):

    # Calculate distance to position
    latitude, longitude, _ = api.get_position()

    latitude = float(latitude)
    longitude = float(longitude)
    olatitude = float(olatitude)
    olongitude = float(olongitude)

    dist = closest = distance(
        latitude,
        longitude,
        olatitude,
        olongitude
    )

    # Run walk
    divisions = closest / step
    dLat = (latitude - olatitude) / divisions
    dLon = (longitude - olongitude) / divisions

    log.info(
        "Walking %f meters. This will take ~%f seconds...",
        dist,
        dist / step
    )

    # Approach at supplied rate
    steps = 1
    s_count = 0
    while dist > epsilon:
        log.info("%f m -> %f m away", closest - dist, closest)
        latitude -= dLat
        longitude -= dLon
        steps %= delay
        if steps == 0:
            api.set_position(
                latitude,
                longitude
            )
        time.sleep(1)
        dist = distance(
            latitude,
            longitude,
            olatitude,
            olongitude
        )
        steps += 1
        s_count += 1
        if s_count%20 == 0:
            api.set_position(
                latitude,
                longitude
            )
            get_poi(api)
            wait(10)

    # Finalize walk
    steps -= 1
    if steps % delay > 0:
        wait(delay - steps)
        api.set_position(
            latitude,
            longitude
        )   


def main():
    # log settings
    # log format
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(module)10s] [%(levelname)5s] %(message)s')
    # log level for http request class
    logging.getLogger("requests").setLevel(logging.WARNING)
    # log level for main pgoapi class
    logging.getLogger("pgoapi").setLevel(logging.INFO)
    # log level for internal pgoapi class
    logging.getLogger("rpc_api").setLevel(logging.INFO)

    config = init_config()
    if not config:
        return

    if config.debug:
        logging.getLogger("requests").setLevel(logging.DEBUG)
        logging.getLogger("pgoapi").setLevel(logging.DEBUG)
        logging.getLogger("rpc_api").setLevel(logging.DEBUG)


    # instantiate pgoapi
    api = pgoapi.PGoApi()
    if config.proxy:
        api.set_proxy({'http': config.proxy, 'https': config.proxy})

    # parse position
    position = util.get_pos_by_name(config.location)
    if not position:
        log.error('Your given location could not be found by name')
        return
    elif config.test:
        return

    # set player position on the earth
    api.set_position(*position)

    # new authentication initialitation
    if config.proxy:
        api.set_authentication( \
		provider = config.auth_service, \
		username = config.username, \
		password = config.password, \
		proxy_config = {'http': config.proxy, 'https': config.proxy}\
	)
    else:
        api.set_authentication( \
		provider = config.auth_service, \
		username = config.username, \
		password = config.password
	)
    last_location = 0
    print ' '
    while True:
        last_location = next_stop(api, last_location, config.username) 
        print " "
        log.info("[Position] Now arrived at " + \
            str(api.get_position()[0] )+ ", "+\
            str(api.get_position()[1]) \
        )
        get_poi( api )
        wait(10)        

def get_poi( api ):    
    poi = {'pokemons': {}, 'forts': [], 'spawn_points': {}}
    position = api.get_position()
    cell_ids = util.get_cell_ids( position[0], position[1] )
    timestamps = [0,] * len(cell_ids)
    response_dict = api.get_map_objects(\
	latitude = position[0], longitude = position[1], \
	    since_timestamp_ms = timestamps, cell_id = cell_ids
    )
    if (response_dict['responses']):
        if 'status' in response_dict['responses']['GET_MAP_OBJECTS']:
            if response_dict['responses']['GET_MAP_OBJECTS']['status'] == 1:
                for map_cell in response_dict['responses']['GET_MAP_OBJECTS']['map_cells']:
                    if 'catchable_pokemons' in map_cell:
                        for pokemons in map_cell['catchable_pokemons']:
                            print pokemons
                    if 'wild_pokemons' in map_cell:
                        for pokemon in map_cell['wild_pokemons']:
                            pokekey = get_key_from_pokemon(pokemon)
                            pokemon['hides_at'] = (time.time() + pokemon['time_till_hidden_ms']/1000)
                            poi['pokemons'][pokekey] = pokemon
                            poi['spawn_points'][pokekey] = {\
                                 'id' : pokekey,\
                                 'latitude': str(pokemon["latitude"]), \
                                 'longitude': str(pokemon["longitude"]) \
                            }
                            #print str(pokekey) + "\r\n\t"+ \
                			#	str(pokemon["spawn_point_id"]) + "\r\n\t" + \
				            #    str(pokemon["latitude"]) + ", " + str(pokemon["longitude"]) +"\r\n\t" + \
                			#	str(pokemon["pokemon_data"]["pokemon_id"]) + "\r\n\t" + \
                			#	str(pokemon["hides_at"]) + "\r\n"
                        insert_data( poi['pokemons'] )
                        insert_spawn( poi['spawn_points'] )

    
def insert_data(poks):
    if( len(poks) == 0 ):
	return
    log.info( "[Found] There are " + str(len(poks)) + " pokemons around here !" )
    db = MySQLdb.connect( "localhost", "root", "pokemon", "pokemon" )
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

    db = MySQLdb.connect( "localhost", "root", "pokemon", "pokemon" )
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



def next_stop(api, lastLocation, profile):
    file = str('location/'+str(profile))
    line_count = num_lines = sum(1 for line in open(file))
    with open( file ) as f:
        lines = f.readlines()
    while True:
        r = randint(0,(line_count-1))
        if r <> lastLocation:
            lastLocation = r
            break
    pos = lines[r].replace("\n","")
    pos = pos.split(",")
    walkTo( api, pos[0], pos[1] )
    return lastLocation 



if __name__ == '__main__':
    lastLocation = 0
    main()


import time
from utils import *
from time import sleep
from random import randint
from challengekit import *
from pgoapi import utilities as util

#{'responses': 
#{'CHECK_CHALLENGE': 
#{'challenge_url': u'https://pgorelease.nianticlabs.com/plfe/281/captcha/C79525F6CE264B49FEB7AD66195F178B', 'show_challenge': True}}
#   , 'status_code': 1
#   , 'platform_returns': [{'type': 6, 'response': 'CAE='}],
#   'request_id': 990451584812974100L}
 
def check_challenge(botid, api):
    wait(3)
    while True:
        challenge = api.check_challenge()
        if "challenge_url" not in challenge["responses"]["CHECK_CHALLENGE"]:
            break
        challenge_url = challenge["responses"]["CHECK_CHALLENGE"]["challenge_url"]
        challenge_time = challenge["request_id"]
        if len( challenge_url ) < 5:
            print "Challenge passed! "
            break
        requestNewChallenge(botid, challenge_time, challenge_url)
        print challenge_url
        while True:
            results = checkTokenUpdate(challenge_time)
            if len(results[0]) > 10 :
                api.verify_challenge( token = results[0] )
                break
            elif results[0] == "expire":
                break

def get_poi( api ):    
    poi = {'pokemons': {}, 'forts': [], 'spawn_points': {}}
    position = api.get_position()
    cell_ids = util.get_cell_ids( position[0], position[1] )
    timestamps = [0,] * len(cell_ids)
    response_dict = api.get_map_objects(\
	    latitude = position[0], longitude = position[1], \
	    since_timestamp_ms = timestamps, cell_id = cell_ids \
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



def walkTo(api, log, olatitude, olongitude, epsilon=10, step=7.5, delay=10):
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
        sleep(1)
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

def next_stop(api, log, lastLocation, profile):
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
    walkTo( api, log, pos[0], pos[1] )
    return lastLocation 



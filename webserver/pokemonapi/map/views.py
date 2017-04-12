from django.http import HttpResponse
from django.shortcuts import render
import MySQLdb
import time
import json

# Create your views here.
def index(request):

    response = HttpResponse( json.dumps(queryMap()), "Application/json" )
    return response


def queryMap():
    db = MySQLdb.connect("localhost","root","caspar","Pokemon" )
    cursor = db.cursor()
    t = int(round(time.time() * 1000))
    t2 = int(round(time.time()*1000))+15*60*1000
#    sql = "SELECT POKEID, LAT, LNG, EXPIRE FROM Encounter WHERE EXPIRE > '%d'" % (t)
    sql = "SELECT POKEID, LAT, LNG, (EXPIRE + 60*60*24*9*1000) AS EXPIRE  FROM Encounter WHERE (EXPIRE + 60*60*24*9*1000) > '%d' && (EXPIRE + 60*60*24*9*1000) < '%d' LIMIT 30" % (t,t2)
    data = []
    try:
        # Execute the SQL command
        cursor.execute(sql)
    
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
            # Now print fetched result
	    data += [{0:row[0], 1:row[1], 2:row[2], 3:row[3]}]
    except Exception, e:
       return "Error: unable to fecth data"+str(e)

    # disconnect from server
    db.close()
    return data

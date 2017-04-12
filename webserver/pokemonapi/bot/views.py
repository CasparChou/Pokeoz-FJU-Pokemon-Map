from django.http import HttpResponse
from django.shortcuts import render
import MySQLdb
import time
import json

# Create your views here.
def index(request):

    response = HttpResponse( json.dumps(queryBot()), "Application/json" )
    return response


def queryBot():
    db = MySQLdb.connect("localhost","root","caspar","Pokemon" )
    cursor = db.cursor()
    t = int(round(time.time() * 1000)) - 15*100
    sql = "SELECT DISTINCT BOTID, LAT, LNG, RECORDTIME FROM Record WHERE RECORDTIME > NOW()-20 GROUP BY BOTID ORDER BY BOTID, RECORDTIME DESC;"
    data = []
    try:
        # Execute the SQL command
        cursor.execute(sql)
    
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
            # Now print fetched result
	    data += [{0:row[0], 1:row[1], 2:row[2]}]
    except Exception, e:
       return "Error: unable to fecth data"+str(e)

    # disconnect from server
    db.close()
    return data

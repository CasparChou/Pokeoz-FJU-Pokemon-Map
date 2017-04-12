from django.http import HttpResponse
from django.shortcuts import render
import MySQLdb
import time
import json

# Create your views here.
def index(request):

    response = HttpResponse( json.dumps(queryLure()), "Application/json" )
    return response


def queryLure():
    return ""
    db = MySQLdb.connect("localhost","root","caspar","Pokemon" )
    cursor = db.cursor()
    t = int(round(time.time() * 1000))
    sql = "SELECT STOPID, LAT, LNG FROM Lure WHERE RECORETIME > (NOW()-60)"
    data = []
    try:
        # Execute the SQL command
        cursor.execute(sql)
    
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
            # Now print fetched result
	    data += [{
		"id":row[0],
		"lat":row[1],
		"lng":row[2],
		}]
    except Exception, e:
       return "Error: unable to fecth data"+str(e)

    # disconnect from server
    db.close()
    return data

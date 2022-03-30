# Python 3.x
# Uses private data from research
# Uses private API access from Google
# Identifies schools anddstudednts in certain latitudes and longitudes
# Records the route from one location to another
# This was maded without access to the real data, thus begins by requesting the headers of the actual  data.

# -------------------------------------
# -------------------------------------
# COMPLETE HERE:

id_ind =    'DISTRICT' #header of location id 
id_school = 'SchoolID' #header of school id
from_lat =  'LAT' #header of location's address
from_lon =  'LON' #header of location's address
to_lat =    'g_lat' #header of school's address
to_lon =    'g_lon' #header of school's address
# -------------------------------------
# -------------------------------------

# this verifies the previous information:
if len(id_ind)<1 or len(id_school)<1 or len(from_lon) <1 or len(from_lat)<1 or len(to_lon)<1 or len(to_lat)<1 :
    print('please input the following variable name/header')
    id_ind = input('Name of individuals ID variable in file >').strip()
    id_school = input('Name of school ID variable in file >').strip()
    from_lat = input('Name of individual latitute column in file >').strip()
    from_lon = input('Name of individual longitude column in file >').strip()
    to_lat = input('Name of destination latitute column in file >').strip()
    to_lon = input('Name of destination longitude column in file >').strip()

###if len(client)==0 :
###    client = input('Insert Google client >').strip()
###	   crypto = input('Insert Google crypto key >').strip()

# -------------------------------------
# Block 1

import datetime
import time
# loads libraries for data management.
try : import pandas as pd
except : print('error loading pandas library')
try : import numpy as np
except : print('error loading numpy library')
# loads Google Maps library.
try : import googlemaps
except : print('error loading googlemaps library')

# load data files with geolocations.

df = pd.ExcelFile('data.xlsx').parse('data')

print('File loaded. Begin scrapping')

try : gmaps = googlemaps.Client(key="")
except: gmaps = googlemaps.Client(client_id=input('Try Client ID again. >').strip(), client_secret=input('Try secret crypto key again>').strip())

# API must have geocode and geolocation enabled.
# https://console.developers.google.com/projectselector/apis/api/directions_backend?supportedpurview=project
# Look for "geo" at APIs' Library.
# check enabling with:
# https://maps.googleapis.com/maps/api/directions/json?origin=75+9th+Ave+New+York,+NY&destination=MetLife+Stadium+1+MetLife+Stadium+Dr+East+Rutherford,+NJ+07073&mode=transit&arrival_time=1391374800&key=AIzaSyBjQNWb1m_PII_gykiWAhTVfsy1GCozd94


# -------------------------------------
# -------------------------------------
# Block 2

start_time = time.time()
rows = []

for n in range(len(df)) :
    from_1 = df[from_lat][n], df[from_lon][n]
    to_1 = df[to_lat][n], df[to_lon][n]
    id_to = df[id_school][n]
    # Request directions via public transit
    directions_result = gmaps.directions(from_1,
                                         to_1,
                                         mode="transit",
                                         arrival_time=datetime.datetime(2018, 3, 30, 8))
    data = {}
    data[id_ind] = df[id_ind][n]
    data[id_school] = id_to
    data[from_lat] = df[from_lat][n]
    data[from_lon] = df[from_lon][n]
    data[to_lat] = df[to_lat][n]
    data[to_lon] = df[to_lon][n]
    try : data['nsteps'] = len(directions_result[0]['legs'][-1]['steps']); data['arrival_time'] = directions_result[0]['legs'][0]['arrival_time']['value']; data['arrival_time1'] = directions_result[0]['legs'][0]['arrival_time']['text']
    except : continue
    try :
        data['departure_time'] = directions_result[0]['legs'][0]['departure_time']['value']
        data['departure_time1'] = directions_result[0]['legs'][0]['departure_time']['text']
    except : continue
    data['distance_mts'] = directions_result[0]['legs'][0]['distance']['value']
    data['duration_sec'] = directions_result[0]['legs'][0]['duration']['value']
    data['steps_mode'] = []
    data['transit_type'] = []
    for k in directions_result[0]['legs'][0]['steps'] :
        data['steps_mode'].append(str(k['travel_mode']))
        # create dummy for type of travel
        data[k['travel_mode']] = 1
        if k['travel_mode'] == 'WALKING' :
            # sum distance and duration walking
            data['distance_walking'] = +k['distance']['value']
            data['duration_walking'] = +k['duration']['value']
            # describe step (to keep order)
            data['step_'+str(directions_result[0]['legs'][0]['steps'].index(k))] = k['travel_mode']
        elif k['travel_mode'] == 'TRANSIT' :
            # sum distance and duration not walking
            data['distance_transit'] = +k['distance']['value']
            data['duration_transit'] = +k['duration']['value']
            data['transit_stops'] = +k['transit_details']['num_stops']
            data['transit_type'].append(str(k['transit_details']['line']['vehicle']['type']))
            # Sum distance and duration in given vehicle
            data['distance_'+k['transit_details']['line']['vehicle']['type']] = +k['distance']['value']
            data['duration_'+k['transit_details']['line']['vehicle']['type']] = +k['duration']['value']
            # Vehicle details
            data['step_'+str(directions_result[0]['legs'][0]['steps'].index(k))] = k['transit_details']['line']['vehicle']['type']
            data['step_'+str(directions_result[0]['legs'][0]['steps'].index(k))+'_headsign'] = k['transit_details']['headsign']
            try : data['step_'+str(directions_result[0]['legs'][0]['steps'].index(k))+'_name'] = k['transit_details']['line']['name']
			except : data['step_'+str(directions_result[0]['legs'][0]['steps'].index(k))+'_name'] = ""
            if "short_name" in k['transit_details']['line'] : data['step_'+str(directions_result[0]['legs'][0]['steps'].index(k))+'_shortname'] = k['transit_details']['line']['short_name']
            # create dummy for type of travel
            data[k['transit_details']['line']['vehicle']['type']] = 1
    rows.append(data)

#save
df2 = pd.DataFrame.from_dict(rows, orient='columns')
df2.to_csv('results.csv', sep=';')

print(time.time() - start_time)
print('The End.')

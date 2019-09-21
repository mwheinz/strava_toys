#! /usr/bin/env python

#
# Retrieves the last N days of Strava activities for 
# an athlete. You have to provide your own client_id,
# client_secret and client_code. See below for more details.
# 
import datetime
import sys
from stravalib.client import Client
from stravalib import unithelper

#
# Magic cookies specifying me, Michael Heinz. If you are
# not Michael Heinz you need to go to developers.strava.com and 
# github.com/hozn/stravalib and get your own magic cookies.
#
# I'm not sure if that client_code will expire but it might. It's 
# an OAUTH2 hack.
#
client_id = NNNNN
client = Client()
client_secret="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

#
# This is a hack to generate the client code.
# Nota bene: Strava docs indicate I might need a new code every 6 hours?
# Could be a pain.
#
#authorization_url=client.authorization_url(client_id=client_id,
#	redirect_uri='http://127.0.0.1:8000/authorization')
#
#print(authorization_url)
#
client_code="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

#
# Magic cookies specifying what data I want back. Strava doesn't seem to 
# document these. When gear is None, returns all gear.
#
types = [ "time", "distance", "heartrate", "temp" ]
gear = None

#
# Date range to retrieve. Defaults to 2 weeks, but can be overridden
# by providing a different # of days in the command line.
#
numdays = 14
if (len(sys.argv) > 1):
	numdays=int(sys.argv[1])
now=datetime.datetime.now()
then=now - datetime.timedelta(numdays)

#
# Authenticate with Strava.
#
token_response = client.exchange_code_for_token(client_id=client_id,
	client_secret=client_secret, code=client_code)

client.access_token = token_response['access_token']
client.refresh_token = token_response['refresh_token']
client.expires_at = token_response['expires_at']

athlete = client.get_athlete()
print("Retrieving records of the past {days} days for {id}: {firstname} {lastname}".format(
	days=numdays, id=athlete.id,
	firstname=athlete.firstname, lastname=athlete.lastname))

activities = list(client.get_activities(after=then, before=now))
activities.reverse()
for activity in activities:
	if (activity.gear_id is None):
		gear_name = "N/A"
	else: 
		if ((gear is None) or gear.id != activity.gear_id):
			gear = client.get_gear(activity.gear_id)
		gear_name = gear.name

	distance=unithelper.miles(activity.distance).get_num()
	speed=unithelper.miles_per_hour(activity.average_speed).get_num()
	print("{dt}, , {bike}, {distance:.2f}, {speed:.1f}, {time}, \"{name}\", {pr} PRs".format(
	dt=activity.start_date.strftime("%m/%d/%y %H:%M"), bike=gear_name, distance=distance,
	speed=speed, time=activity.moving_time, name=activity.name,
	pr=activity.pr_count))

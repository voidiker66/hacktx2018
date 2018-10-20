import requests
import datetime

def get_time_utc(time):
	return str(datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S').strftime("%B %d, %Y at %H:%M"))
def get_events(latitude, longitude):
	return requests.get(
	    "https://api.sandbox.amadeus.com/v1.2/points-of-interest/yapq-search-circle?apikey=rBYxMyKDkSqumoGZthxpnBZyHbwSTd0o&latitude=" + latitude + "&longitude=" + longitude + "&radius=42&lang=EN",
	    verify = True,  # Verify SSL certificate
	)
j = get_events(str(49.10), str(-123.11934)).json()
print(j)
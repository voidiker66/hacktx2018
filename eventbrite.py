import requests
import datetime

def get_time_utc(time):
	return str(datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S').strftime("%B %d, %Y at %H:%M"))
def get_events(location, start, end):
	return requests.get(
	    "https://www.eventbriteapi.com/v3/events/search?sort_by=best&location.address=" + location
	    + '&start_date.range_start=' + start + '&start_date.range_end=' + end,
	    headers = {
	        "Authorization": "Bearer 7PW4452MWTLYVZVWNH3K",
	    },
	    verify = True,  # Verify SSL certificate
	)
j = get_events('dallas', datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')).json()
print(j)
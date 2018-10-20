import requests
response = requests.get(
    "https://www.eventbriteapi.com/v3/events/search?location.address=London,UnitedKingdom",
    headers = {
        "Authorization": "Bearer 7PW4452MWTLYVZVWNH3K",
    },
    verify = True,  # Verify SSL certificate
)
j = response.json()
for e in j['events']:
	print(e['name']['text'])
	print(e['start']['local'] + ' - ' + e['end']['local'])
	if e['is_free']:
		print('Free')
	else:
		print(e['fee'])
	quit()
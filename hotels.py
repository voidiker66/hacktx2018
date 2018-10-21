import requests
import os

apikey = os.getenv("AMADEUS_KEY", "")

def getHotels(apikey, airportCode, checkIn, checkOut):
    payload = {'apikey': apikey, 'location': airportCode, 'check_in': checkIn, 'check_out': checkOut}
    r = requests.get("https://api.sandbox.amadeus.com/v1.2/hotels/search-airport", params=payload)
    r = r.json()
    print(r['results'][0]['total_price']['amount'])
    return(r['results'])

getHotels(apikey, "IAH", "2018-10-31", "2018-11-02")

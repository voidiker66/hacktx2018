import requests
import pymongo
from bson.objectid import ObjectId

from airlines.airport import get_airport

def get_user(email):
    if not isinstance(email, str):
        return TypeError("email should be a string.")
    r = requests.get("https://mock-aa.herokuapp.com/user?email=" + email)
    if r.status_code != 200:
        return ValueError("Bad email, user not found.")
    return r.json()

def get_user_id(email):
    return get_user(email)['_id']

def register_user(first_name, last_name, email, gender="Other", aadv=None):
    if not isinstance(first_name, str):
        return TypeError("first_name should be a string.")
    if not isinstance(last_name, str):
        return TypeError("last_name should be a string.")
    if not isinstance(email, str):
        return TypeError("email should be a string.")
    if not (gender == 'Male' or gender == 'Female' or gender == 'Other'):
        return ValueError("gender should be a string of one of the form: "
            "Male, Female, or Other")
    req_string = "?firstName=" + first_name + "&lastName=" + last_name + \
            "&email=" + email + "&gender=" + gender
    if aadv:
        req_string += '&aadvantageNumber=' + aadv
    r = requests.post("https://mock-aa.herokuapp.com/user" + req_string)
    if r.status_code == 400:
        print ("User could not be created: " + r.text)
    elif r.status_code != 200:
        raise ValueError("User could not be created.")
    return r.json()

def reserve_trip(user_id, trip_id1, trip_id2):
    r = requests.post("https://mock-aa.herokuapp.com/reservation?userId=" \
            + user_id + "&flightIds=" + trip_id1 + "," + trip_id2)
    if r.status_code != 200:
        print ("Could not make reservation: " + r.text)
    return r.json()

def get_user_trips(user_id):
    client = pymongo.MongoClient("mongodb://test:test1234@ds237563.mlab.com:37563/heroku_795sgmrw")
    db = client.heroku_795sgmrw
    col = db.reservation
    fli = db.flight
    cursor = col.find({"userId" : user_id})
    reservations = {}
    for r in cursor:
        records = r['flightIds']
        cur_res = []
        for re in records:
            re = re.lstrip("[").rstrip("]")
            trip = fli.find_one(ObjectId(re))
            trip['origin'] = get_airport(trip['origin'])['city']
            trip['destination'] = get_airport(trip['destination'])['city']
            cur_res.append(trip)
        reservations[r['recordLocator']] = cur_res
    return reservations

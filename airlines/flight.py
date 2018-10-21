import datetime as dt
import pytz
import requests

import airlines.airport as apt

def datetime_parser(datetime):
    if datetime[-1] == 'Z':
        datetime = dt.datetime.strptime(datetime, "%Y-%m-%dT%H:%MZ")
        datetime = datetime.replace(tzinfo=dt.timezone.utc)
    else:
        a, b, c = datetime.rpartition(':')
        datetime = a + c
        datetime = dt.datetime.strptime(datetime, "%Y-%m-%dT%H:%M%z")
    return datetime

def to_utc(datetime):
    return datetime.astimezone(pytz.utc)

####### Use these functions to serialize time and deserialize time #######
def datetime_to_utcstring(datetime):
    datetime = to_utc(datetime)
    return datetime.strftime("%Y-%m-%dT%H:%M%z")

def utcstring_to_datetime(datetime_str):
    return dt.datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M%z")

def datetime_to_cststring(datetime):
    datetime = datetime.astimezone(pytz.timezone('America/Chicago'))
    return datetime.strftime("%Y-%m-%d %H:%M")
##########################################################################

def get_flights(origin_code, destination_code, date):
    if not origin_code in apt.AIRPORTS.__members__:
        raise ValueError("origin is not a valid airport code.")
    if not destination_code in apt.AIRPORTS.__members__:
        raise ValueError("destination is not a valid airport code.")
    r = requests.get('https://mock-aa.herokuapp.com/docs/flights?origin='
        + origin_code + "&destination=" + destination_code + "&date="
        + date)
    if r.status_code != 200:
        print(origin_code)
        print(destination_code)
        print(r.text)
        raise ValueError("failed to get flights.")
    return r.json()

def get_dest_flights(origin, destination, start_date,
        end_date, count_limit=10):
    """Returns a list of flights

    Parameters
    ----------
    origin
        type str; start location for the flight
    destination
        type str; end location for the flight
    start_date
        type str; earliest start date for the flight in 'yyyy-mm-ddTHH:MM:SS' format
    end_date:
        type str; end date for the trip in 'yyyy-mm-ddTHH:MM:SS' format
    count_limit
        type int; maximum number of flights

    Returns
    -------
    list
        a list of possible flights from origin to destination within the
        duration_days, with a size of count_limit or less
    """
    flights = []

    # TODO: should our list of possible flights start from datetime now.
    current_dt = dt.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S") \
        .replace(tzinfo=dt.timezone.utc)
    iter_dt = current_dt
    end_dt = dt.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S") \
        .replace(tzinfo=dt.timezone.utc)
    ###################################################################

    origin_code = apt.get_airport_code(origin)
    destination_code = apt.get_airport_code(destination)
    while iter_dt < end_dt and count_limit > 0:
        possible_flights = get_flights(origin_code, destination_code, \
            iter_dt.strftime("%Y-%m-%d"))

        for flight in possible_flights:
            depart_time = datetime_parser(flight['departureTime'])
            flight['departureUTCTime'] = datetime_to_utcstring(depart_time)
            arrival_time = datetime_parser(flight['arrivalTime'])
            flight['arrivalUTCTime'] = datetime_to_utcstring(arrival_time)

            if depart_time >= current_dt and arrival_time <= end_dt \
                    and count_limit > 0:
                flights.append(flight)
                count_limit -= 1

        iter_dt += dt.timedelta(days=1)

    return flights

def get_return_flights(origin, destination, start_date,
        end_date, count_limit=10):

    flights = []

    # TODO: should our list of possible flights start from datetime now.
    current_dt = dt.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S") \
        .replace(tzinfo=dt.timezone.utc)
    end_dt = dt.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S") \
        .replace(tzinfo=dt.timezone.utc) + dt.timedelta(seconds=1)
    iter_dt = end_dt - dt.timedelta(seconds=1)
    ###################################################################

    origin_code = apt.get_airport_code(origin)
    destination_code = apt.get_airport_code(destination)
    while current_dt < iter_dt and count_limit > 0:
        possible_flights = get_flights(origin_code, destination_code, \
            iter_dt.strftime("%Y-%m-%d"))

        for flight in reversed(possible_flights):
            depart_time = datetime_parser(flight['departureTime'])
            flight['departureUTCTime'] = datetime_to_utcstring(depart_time)
            arrival_time = datetime_parser(flight['arrivalTime'])
            flight['arrivalUTCTime'] = datetime_to_utcstring(arrival_time)

            if depart_time >= current_dt and arrival_time < end_dt \
                    and count_limit > 0:
                flights.append(flight)
                count_limit -= 1

        iter_dt -= dt.timedelta(days=1)

    return flights

def get_flights_view(flights):
    flights_view = []
    for flight in flights:
        flight_view = {}
        flight_view['flightNumber'] = flight['flightNumber']
        flight_view['departureTime'] = datetime_to_cststring(
            utcstring_to_datetime(flight['departureUTCTime']))
        flight_view['arrivalTime'] = datetime_to_cststring(
            utcstring_to_datetime(flight['arrivalUTCTime']))
        flight_view['cost'] = flight['cost']
        flight_view['mongoid'] = flight['_id']
        flights_view.append(flight_view)
    return flights_view

def get_flight_average_cost(origin, destination, start_date,
        end_date, count_limit=10):
    flightd = get_dest_flights(origin, destination, start_date,
        end_date, count_limit)
    flightview = get_flights_view(flightd)
    costd = 0
    for flight in flightview:
        costd += float(flight['cost'])
    costd = costd/len(flightview)
    flightview = get_dest_flights(origin, destination, start_date, end_date, count_limit)
    costa = 0
    for flight in flightview:
        costa += float(flight['cost'])
    costa = costa/len(flightview)
    return (costd + costa)/2

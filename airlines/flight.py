import enum
import requests

# Possible airport codes for current project
class AIRPORTS(enum.Enum):
    DFW = 1
    LAX = 2
    MIA = 3
    PHL = 4
    ORD = 5
    JFK = 6
    LHR = 7
    HKG = 8

def get_airport(code):
    """get airport information from airport code.

    Parameter
    ---------
    code
        type str, airport code.

    Return
    ------
    dict
        airport information in the form of a dict.
    """

    if not isinstance(code, str):
        raise TypeError("'code' argument should be of type str")

    r = requests.get('https://mock-aa.herokuapp.com/airports?code=' + code)
    if r.status_code != 200:
        raise ValueError("Failed request: " + str(r.status_code))
    info = r.json()
    size = len(info)
    if not size:
        raise ValueError("No return airport values.")
    if len(info) != 1:
        raise ValueError("Invalid return airport values.")
    return info[0]

def get_cities():
    """Returns a dict of possible cities and their information.

    Parameters
    ----------
    None

    Returns
    -------
    dict
        a dict of possible cities and their information.
    """

    global _cities
    try:
        if _cities:
            return _cities
    except NameError:
        pass

    _cities = {}
    for airport in AIRPORTS:
        airport_code = airport.name
        info = get_airport(airport_code)
        _cities[info['city']] = info

    return _cities


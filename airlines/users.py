import requests

def get_user(email):
    if not isinstance(email, str):
        return TypeError("email should be a string.")
    r = requests.get("https://mock-aa.herokuapp.com/user?email=" + email)
    if r.status != 200:
        return ValueError("Bad email, user not found.")
    return r.json()

def get_user_id(email):
    return get_user(email)['id']

def register_user(first_name, last_name, email, gender="Other", aadv=None):
    if not isinstance(first_name, str):
        return TypeError("first_name should be a string.")
    if not isinstance(last_name, str):
        return TypeError("last_name should be a string.")
    if not isinstance(email, str):
        return TypeError("email should be a string.")
    if not (gender == 'Male' or gender == 'Female' or gender == 'Other'):
        return ValueError("gender should be a string of one of the form: Male, Female, or Other")
    data = {}
    data['firstName'] = first_name
    data['lastName'] = last_name
    data['email'] = email
    data['gender'] = gender
    if aadv:
        data['aadvantageNumber'] = aadv
    r = requests.post("https://mock-aa.herokuapp.com/user", json=data)
    if r.status_code == 400:
        print ("User could not be created: " + r.text)
    elif r.status_code != 200:
        raise ValueError("User could not be created.")
    return r.json()

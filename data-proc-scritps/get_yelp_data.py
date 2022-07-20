import json
from unittest.main import main
import requests

def make_request(location, term, offset):
    url = "https://api.yelp.com/v3/businesses/search?location=" + location + "&term=" + term + "&limit=50&offset=" + str(offset)
    payload={}
    headers = {
        'Authorization': 'Bearer grHa-dTyBlD391sI-bibqcP0W8ZEvNpGkGc6Usn1b1asi11PAH-oP6Lj5wnlw6A-mb8x-Sz_DnhDplt7NTex59LfEdCbfFGTskgPyLUy0KYGvyN5Bp3zTOeHUHoJYnYx'
    }  
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    return data['businesses']

def run():
    ids = {}
    locations = ["manhattan", "brooklyn", "queens", "bronx", "boston"]
    cuisines = ["indian", "mexican", "thai", "chinese", "italian"]
    for location in locations:
        for cuisine in cuisines:
            i = 0
            total = 0
            while i < 1000:
                businesses = make_request(location, cuisine, i)
                for business in businesses:
                    if business["id"] not in ids:
                        total += 1
                        ids[business["id"]] = True
                        path = "/Users/aatman/nyu/Sem 2/CC/assignment1/data/" + location + "/" + cuisine + "/" + business["id"] + ".json"
                        with open(path, "w") as outfile:
                            json.dump(business, outfile)
                i = i + 50
            print(location, "-", cuisine, "-", total)

run()
import re
import json

import requests
import furl
from geojson import LineString
import geojson

config = {}

write_config = False

with open("config.json", "r", encoding="utf-8") as config_file:
    config = json.load(config_file)

for place in config['places']:
    if "latitude" in place and "longitude" in place:
        print(f"Loading Lat/Long for {place['name']}")
    else:
        write_config = True
        print(f"Lat/Long not found for {place['name']}, searching...", end="")
        search_url = furl.furl(config['urls']['search'])
        search_url /= place['search_text'] + ".json"
        search_url.args['country'] = "us"
        search_url.args['language'] = "en"
        search_url.args['limit'] = "1"
        search_url.args['access_token'] = config['keys']['access_token']
        response = requests.get(search_url.url)

        if response.status_code != 200:
            raise LookupError()

        latitude = response.json()['features'][0]['center'][0]
        longitude = response.json()['features'][0]['center'][1]

        print(f"Found: {latitude}, {longitude}")

        place['latitude'] = latitude
        place['longitude'] = longitude


if write_config:
    with open("config.json", "w",encoding="utf-8") as file:
        json.dump(config, file, indent=4)
       

# Directions
places = config['places']

direction_type = "home-to-work"

directions_info = [direction for direction in config['directions'] if direction['name'] == direction_type][0]

# place_from = [place for place in places if place['name'] == directions_info['from']][0]
place_from = requests.get("https://0t64mkt9ug.execute-api.us-east-1.amazonaws.com/default/get_will_location").json()
place_to = [place for place in places if place['name'] == directions_info['to']][0]


f = furl.furl(config['urls']['directions'])
f /= f"{place_from['longitude']},{place_from['latitude']};" + \
        f"{place_to['longitude']},{place_to['latitude']}"

f.args['alternatives'] = "false"
f.args['continue_straight'] = "false"
f.args['geometries'] = "polyline"
f.args['overview'] = "full"
f.args['steps'] = "false"
f.args['access_token'] = config['keys']['access_token']


dir_resp = requests.get(f.url)
best_route = dir_resp.json().get("routes")[0]
duration = int(float(best_route.get("duration")) / 60)
print(f"Estimated Duration: {duration} minutes")

polyline = dir_resp.json().get("routes")[0].get("geometry")


# Image Map
f = furl.furl(config['urls']['static'])

f /= f"pin-l-home({place_from['longitude']},{place_from['latitude']})," + \
        f"pin-l-{place_to['icon']}({place_to['longitude']},{place_to['latitude']})," + \
        f"path({polyline})"
f /= "auto"
f /= "900x700@2x"
f.args['access_token'] = config['keys']['access_token']

print(f.url)

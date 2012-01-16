# -*- coding: utf-8 -*-
import json
import requests
import urllib
from urllib import urlopen
import codecs
import time
from ski_parse import get_conditions

url = u"http://maps.googleapis.com/maps/api/geocode/json?address={0}&sensor=false"

def format_spaces(input):
    return input.replace(" ", "+")

def get_coords(place):
    place = format_spaces(place)
    request = url.format(place)
    response = urlopen(request.encode("utf8"))
    j = json.loads(response.read())
    try:
        coords = j["results"][0]["geometry"]["location"]
    except:
        print j
    return coords["lat"], coords["lng"]

if __name__ == '__main__':
    with open("ski_locations.txt") as f:
        file = codecs.getreader("utf-8")(f).read()
        addresses = json.loads(file)

    #locations = []
    locations = get_conditions()
    for track in addresses:
        name, address = track.values()
        lat, lng = get_coords(address)
        #locations.append({
                            #"name": name,
                            #"address": address,
                            #"latitude": lat,
                            #"longitude": lng
                         #})
        locations[name]["latitude"] = lat
        locations[name]["longitude"] = lng
        #locations.append(u"{}\t {}\t {}".format(name, lat, lng))
        #print name, lat, lng

    #with open("ski_coords.tsv", "w") as file:
        #for l in locations:
            #file.write(l.encode("utf8"));
            #file.write("\n")

    with open("../ski/ski_coords.json", "w") as file:
        out =  json.dumps(locations, indent=4, sort_keys=True, ensure_ascii=False)
        file.write(out.encode("utf8"))


    #for i,l in enumerate(lines):
        #name, adresse = l.split(': ')
        #adresse = adresse.replace('<br>', ' ')
        #lat, lng = get_coords(adresse)
        #out = {
                #"name": name,
                #"latitude": lat,
                #"longitude": lng,
                #"adresse": adresse
              #}
        #locations.append(out)
        #if i%5:
            #time.sleep(0.5)
        ##print json.dumps(out, indent=4, sort_keys=True, ensure_ascii=False), ","
        ##for key, val in out.items():
            ##print key, val
    #print json.dumps(locations, indent=4, sort_keys=True, ensure_ascii=False)

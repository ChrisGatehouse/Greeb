#!/usr/bin/python3.4
# Copyright (c) 2017 Chris Gatehouse

import urllib.request
import json

'''
the Weather class will get data from the Weather Underground API and allow for retrieval of the information 
with the methods
'''

class Weather(object):
    def __init__(self):
        url = 'http://api.wunderground.com/api/c4baab249321b3d9/geolookup/conditions/q/OR/97116.json'
        url2 = 'http://api.wunderground.com/api/c4baab249321b3d9/astronomy/q/OR/97116.json' #for sunrise/sunset information
        req = urllib.request.Request(url)

        r = urllib.request.urlopen(req).read()
        content = json.loads(r.decode('utf-8'))

        #make the attributes a little private, use the methods to get values
        self.__city = content['current_observation']['display_location']['city']
        self.__temp_f = content['current_observation']['temp_f']
        self.__weather = content['current_observation']['weather']

    def get_city(self):
        return self.__city

    def get_tempf_float(self):
        return self.__temp_f

    def get_tempf_string(self):
        return str(self.__temp_f)

    def get_weather(self):
        return self.__weather

if __name__ == "__main__":
    w = Weather()
    print(w.get_city() + '\n' + w.get_tempf_string() + 'F\n' + w.get_weather())


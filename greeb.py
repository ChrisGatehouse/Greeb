#!/usr/bin/python3.4
# Copyright (c) 2017 Chris Gatehouse

#TODO Implement a config file to load any globals
RASPBERRY_PRESENT = True #TODO implement a check to see if we are actually running on a Raspberry
TEST_MODE = False #some conditions prevent test mode from working correctly
HIGH_THRESHOLD = 40.0
LOW_THRESHOLD = 100.0

from tkinter import *
import sys
import os
import random
import time
import threading
import logging
import math
from queue import Queue
from queue import LifoQueue
from random import randint

#non-standard imports
from weather import Weather
from HVACStates import HVACStates

if RASPBERRY_PRESENT:
    from Gpio import Gpio


'''temperatureSensor gets the temperature from the sensor and adds the result to the queue'''


def temperatureSensor(stop_event, temperatureSensor_q):
    if RASPBERRY_PRESENT:
        if not TEST_MODE: #FIX THIS conditional
            while not stop_event.wait(0):  # how often should we bother getting the temperature...
                _tempFile = open("/sys/bus/w1/devices/28-000008e0f944/w1_slave")  #TODO clean this up to work with multiple sensors
                _readFile = _tempFile.read()
                _tempFile.close()
                _data = _readFile.split("\n")[1].split(" ")[9]
                _sensorTemperature = float(_data[2:]) / 1000
                _sensorTemperature = float("{0:.1f}".format((celsius_to_fahrenheit(_sensorTemperature))))
                temperatureSensor_q.put(_sensorTemperature)
        else: #if we set TEST_MODE then start a quick counter to go through temperature faster
            i = 0
            j = 0
            while not stop_event.wait(0):  # how often should we bother getting the temperature...
                if j == 0:
                    i = i + 1
                else:
                    i = i - 1
                if i > 100:
                    j = 1
                if i <= 0:
                    j = 0
                temperatureSensor_q.put(i)
    else:
        logging.warning("NO RASPBERRY PRESENT!")
        logging.warning("using generic temperature up-down counter")
        i = 0
        j = 0
        while not stop_event.wait(.250):
            if j == 0:
                i = i + 1
            else:
                i = i - 1
            if i > 100:
                j = 1
            if i <= 0:
                j = 0
            temperatureSensor_q.put(i)


def relayStates_2(pin, state):
    Gpio.set_output(gp, pin, state)

'''
This is a basic test of the 8 channel relay that is connected to the Raspberry Pi. 
It sets of the GPIO and randomly cycles through the 8 channels of the relay.
This logic will be used elsewhere in Greep to control the GPIO
'''

def relayStates(stop_event, relayStates_q):
    if RASPBERRY_PRESENT:
        if not TEST_MODE:
            i = 0
            while not stop_event.wait(.250):
                i = i + 1  # counter just to display something to show thread is active
                pin_state = randint(0, 1)
                relayStates_q.put(i)
        else:
            i = 0
            while not stop_event.wait(.250):
                # pick a switch at random, and turn it on/off at random
                i = i + 1  # counter just to display something to show thread is active
                pin_state = randint(0, 1)
                #this_pin = Gpio.get_random_pin(gp)
                #logging.debug("Setting pin " + str(this_pin) + " to state " + str(pin_state))
                #Gpio.set_output(gp, this_pin, pin_state)
                
                relayStates_q.put(i)
    else:
        logging.warning("NO RASPBERRY PRESENT!")
        logging.warning("using generic relayStates counter")
        i = 0
        while not stop_event.wait(.150):
            i = i + 1
            relayStates_q.put(i)


'''convert temperature in Celsius to Fahrenheit'''


def celsius_to_fahrenheit(celsius):
    return (celsius * 1.8) + 32


def monitorTemperature(stop_event,temperatureSensor_q):
    currentTemperature = temperatureSensor_q.get()
    return currentTemperature

class Gui(object):
    def __init__(self, relayStates_q, temperatureSensor_q):
        # setup queues
        self.relayStates_q = relayStates_q
        self.temperatureSensor_q = temperatureSensor_q

        # setup gui window elements
        self.master = Tk()
        self.master.wm_title("Greeb in Tkinter")
        self.master.minsize(800, 480)  # Official Raspberry Pi screen resolution

        # define variables to use in gui elements
        self.city = StringVar()
        self.weather = StringVar()
        self.weatherTemperature = StringVar()
        self.weatherTemperature_float = DoubleVar()
        self.sunrise = StringVar()
        self.sunset = StringVar()
        self.currentTemp = StringVar()
        self.genericRelayCounter = StringVar()
        self.genericTemperatureCounter = DoubleVar()
        self.heatState = StringVar()
        self.acState = StringVar()
        self.heatStateBG = StringVar()
        self.acStateBG = StringVar()
        self.highThreshold = DoubleVar()
        self.lowThreshold = DoubleVar()
        
        #set initial temperature thresholds
        self.__set_highThreshold(HIGH_THRESHOLD)
        self.__set_lowThreshold(LOW_THRESHOLD)
  
        #Weather
        self.currentWeatherLabel = Label(self.master, text="Current Conditions")
        self.currentWeatherLabel.place(x=10, y=110)
        
        self.cityLabel = Label(self.master, textvariable=self.weather, justify='center', anchor='center')
        self.cityLabel.place(x=10, y=170)
        
        self.weatherLabel = Label(self.master, textvariable=self.weatherTemperature, justify='center', anchor='center')
        self.weatherLabel.place(x=10, y=150)
        
        self.currentWeatherLabel = Label(self.master, textvariable=self.city, justify='center', anchor='center')
        self.currentWeatherLabel.place(x=10, y=130)
        
        self.sunriseLabel = Label(self.master, text="Sunrise")
        self.sunriseLabel.place(x=10, y=200)
        
        self.currentSunriseLabel = Label(self.master, textvariable=self.sunrise)
        self.currentSunriseLabel.place(x=10, y=225)
        
        self.sunriseLabel = Label(self.master, text="Sunset")
        self.sunriseLabel.place(x=100, y=200)
        
        self.currentSunriseLabel = Label(self.master, textvariable=self.sunset)
        self.currentSunriseLabel.place(x=100, y=225)
        
        #HEATING
        self.heatcurrentbutton = Button(self.master, textvariable=self.highThreshold, state=DISABLED, disabledforeground="black", width=3)
        self.heatcurrentbutton.place(x=250, y=75)
        
        self.heatButton = Button(self.master, text="HEAT", justify='left', width=5, disabledforeground="black", command=self.set_heattemperature)
        self.heatButton.place(x=300, y=75)
        
        self.heatStateButton = Button(self.master, textvariable=self.heatState, width=10, state=DISABLED, disabledforeground="black")
        self.heatStateButton.place(x=350, y=75)

        #COOLING
        self.accurrentbutton = Button(self.master, textvariable=self.lowThreshold, state=DISABLED, disabledforeground="black", width=3)
        self.accurrentbutton.place(x=250, y=200)
        
        self.acButton = Button(self.master, text="AC", width=5, disabledforeground="black", command=self.set_actemperature)
        self.acButton.place(x=300, y=200)
        
        self.acStateButton = Button(self.master, textvariable=self.acState, width=10, state=DISABLED, disabledforeground="black")
        self.acStateButton.place(x=350, y=200)

        #self.relayLabel = Label(self.master, textvariable=self.genericRelayCounter, width=20)
        #self.relayLabel.place(x=150, y=150)

        self.temperatureList = Listbox(self.master, width=10, height=5)
        #not the best place to do this, will slow down the UI generation
        #fahrenheit only at the moment
        i = 0
        tempoffset = 40.0 #lowest temperature allowed
        temprange = [None] * 100
        while i < 61:
            temprange.insert(i, i + tempoffset)
            i = i + 1
        for temp in temprange:
            self.temperatureList.insert(END, temp)
        self.temperatureList.place(x=465,y=110)

        self.currentTemperatureLabel = Label(self.master, text="Temperature", width=10)
        self.currentTemperatureLabel.place(x=300, y=130)
        
        self.temperatureLabel = Label(self.master, textvariable=self.genericTemperatureCounter)
        self.temperatureLabel.place(x=300, y=150)

        # start the reading the queues, self schedules after this initial run
        logging.debug("reading queues")
        self.read_queues()
        self.get_weather()

        #act on current temperature
        if not TEST_MODE and RASPBERRY_PRESENT:
            self.temperatureAction()


    def temperatureAction(self):
        #print("temp action")
        # Gpio.gpio_active_pins = [2, 3, 8, 14, 15, 18, 23, 24]
        # temp pin assignments AC=2, HEAT=3
        temp = self.genericTemperatureCounter.get()
        if temp > HIGH_THRESHOLD and temp > LOW_THRESHOLD:
            logging.debug("Turning heat off")
            if not TEST_MODE and RASPBERRY_PRESENT:
                relayStates_2(3,1)
                relayStates_2(2,0) # Turn on AC, turn off HEAT
            self.__set_heatState("OFF")
            self.__set_acState("ON")
        elif temp < LOW_THRESHOLD and temp < HIGH_THRESHOLD:
            logging.debug("Turning heat on")
            if not TEST_MODE and RASPBERRY_PRESENT:
                relayStates_2(2,1)
                relayStates_2(3,0) # Turn on HEAT, turn off AC
            self.__set_heatState("ON")
            self.__set_acState("OFF")
        else:
            if not TEST_MODE and RASPBERRY_PRESENT:
                relayStates_2(2,1)
                relayStates_2(3,1) # Turn off HEAT, turn off AC, set to IDLE
            self.__set_heatState("IDLE")
            self.__set_acState("IDLE")
        
        self.master.after(1000, self.temperatureAction)


    def read_queues(self):
        self.genericRelayCounter.set(self.relayStates_q.get())
        #self.genericTemperatureCounter.set(self.temperatureSensor_q.get())
        self.genericTemperatureCounter.set(monitorTemperature(stop_event, temperatureSensor_q))

        # schedule to run read queues again in x milliseconds
        self.master.after(1000, self.read_queues)
    
    def get_weather(self):
        self.weatherTemperature.set(weather.get_tempf_string())
        self.weatherTemperature_float.set(weather.get_tempf_float())
        self.city.set(weather.get_city())
        self.weather.set(weather.get_weather())
        self.sunrise.set(weather.get_sunrise())
        self.sunset.set(weather.get_sunset())
        #schedule to run again in 3 minutes, limit of 500 requests per day to api
        self.master.after(180000,self.get_weather)

    def __set_heatState(self, state):
        self.heatState.set(state)
        if state == "ON":
            self.heatStateBG.set("green")
            self.heatStateButton.configure(bg="green")
        else:
            self.heatStateBG.set("red")
            self.heatStateButton.configure(bg="red")
    
    def __set_highThreshold(self,threshold):
        self.highThreshold.set(threshold)
    
    def __set_lowThreshold(self,threshold):
        self.lowThreshold.set(threshold) 
    
    def __set_holdThreshold(self,threshold):
        pass

    def __set_acState(self, state):
        self.acState.set(state)
        if state == "ON":
            self.acStateBG.set("green")
            self.acStateButton.configure(bg="green")
        else:
            self.acStateBG.set("red")
            self.acStateButton.configure(bg="red")

    def get_heatState(self):
        return self.heatState.get()

    def get_acState(self):
        return self.acState.get()
        
    def set_heattemperature(self):
        global HIGH_THRESHOLD 
        HIGH_THRESHOLD = self.temperatureList.get(ACTIVE)
        self.highThreshold.set(HIGH_THRESHOLD)
    
    def set_actemperature(self):
        global LOW_THRESHOLD 
        LOW_THRESHOLD = self.temperatureList.get(ACTIVE)
        self.lowThreshold.set(LOW_THRESHOLD)


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s')

    # create queues
    logging.debug("creating queues")
    relayStates_q = LifoQueue()
    temperatureSensor_q = LifoQueue()

    # define event to stop threads
    stop_event = threading.Event()

    # define threads
    logging.debug("defining threads")
    relay_t = threading.Thread(target=relayStates, name="relayThread",
                                            args=[stop_event, relayStates_q])
    temperatureSensor_t = threading.Thread(target=temperatureSensor, name="temperatureThread",
                                            args=[stop_event, temperatureSensor_q])

    relay_t.daemon = TRUE
    temperatureSensor_t.daemon = TRUE

    # start threads
    logging.debug("starting threads")
    relay_t.start()
    temperatureSensor_t.start()

    weather = Weather()
    
    for state in HVACStates:
        logging.debug(state)

    if RASPBERRY_PRESENT:
        #don't create an instance of Gpio if the Raspberry is not present
        gp = Gpio()
    logging.debug("starting gui")
    gui = Gui(relayStates_q, temperatureSensor_q)
    gui.master.mainloop()

    if 'gp' in locals():
        gp.cleanup_io()

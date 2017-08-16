#!/usr/bin/python3.4
# Copyright (c) 2017 Chris Gatehouse

#TODO Implement a config file to load any globals
RASPBERRY_PRESENT = True #TODO implement a check to see if we are actually running on a Raspberry
TEST_MODE = False
HIGH_THRESHOLD = 91.0
LOW_THRESHOLD = 89.0

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

# https://pypi.python.org/pypi/RPi.GPIO
if RASPBERRY_PRESENT:
    import RPi.GPIO as GPIO


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
                #_sensorTemperature = _sensorTemperature / 1000
                _sensorTemperature = float("{0:.1f}".format((celsius_to_fahrenheit(_sensorTemperature))))
                #_sensorTemperature = format_float(celsius_to_fahrenheit(_sensorTemperature),2)
                temperatureSensor_q.put(_sensorTemperature)
        else:
            while not stop_event.wait(0):  # how often should we bother getting the temperature...
                _tempFile = open("/sys/bus/w1/devices/28-000008e0f944/w1_slave")  #TODO clean this up to work with multiple sensors
                _readFile = _tempFile.read()
                _tempFile.close()
                _data = _readFile.split("\n")[1].split(" ")[9]
                _sensorTemperature = float(_data[2:]) / 1000
                #_sensorTemperature = _sensorTemperature / 1000
                _sensorTemperature = float("{0:.1f}".format((celsius_to_fahrenheit(_sensorTemperature))))
                #_sensorTemperature = format_float(celsius_to_fahrenheit(_sensorTemperature),2)
                temperatureSensor_q.put(_sensorTemperature)
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
                i = i + 1  # counter for fun, just to display something to show thread is active
                pin_state = randint(0, 1)
                #this_pin = Gpio.get_random_pin(gp)
                #logging.debug("Setting pin " + str(this_pin) + " to state " + str(pin_state))
                #Gpio.set_output(gp, this_pin, pin_state)
                relayStates_q.put(i)
        else:
            i = 0
            while not stop_event.wait(.250):  # (True):
                # pick a switch at random, and turn it on/off at random
                i = i + 1  # counter for fun, just to display something to show thread is active
                pin_state = randint(0, 1)
                this_pin = Gpio.get_random_pin(gp)
                logging.debug("Setting pin " + str(this_pin) + " to state " + str(pin_state))
                Gpio.set_output(gp, this_pin, pin_state)
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

def format_float(input, places):
    pass

def monitorTemperature(stop_event,temperatureSensor_q):
    currentTemperature = temperatureSensor_q.get()
    #ISSUE WITH THE FOLLOWING CODE, DO IT IN GUI LOOP FOR NOW: gui does not exist when trying to access
    '''
    if currentTemperature > HIGH_THRESHOLD:
        relayStates_2(3,0)
        relayStates_2(2,1) # Turn on AC, turn off HEAT
        if 'gui' in locals():
            Gui.set_gp_heatState(gui,"OFF")
            Gui.set_gp_acState(gui,"ON")
    elif currentTemperature < LOW_THRESHOLD:
        relayStates_2(2,0)
        relayStates_2(3,1) # Turn on HEAT, turn off AC
        if 'gui' in locals():
            Gui.set_gp_heatState(gui,"ON")
            Gui.set_gp_acState(gui,"OFF")
    '''
    return currentTemperature

class Gui(object):
    def __init__(self, relayStates_q, temperatureSensor_q):
        # setup queues
        self.relayStates_q = relayStates_q
        self.temperatureSensor_q = temperatureSensor_q

        #globals
        #global HIGH_THRESHOLD, LOW_THRESHOLD

        # setup gui window elements
        self.master = Tk()
        self.master.wm_title("Greeb in Tkinter")
        self.master.minsize(800, 480)  # Official Raspberry Pi screen resolution

        #temperature thresholds
        #self.highThreshold = DoubleVar()
        #self.lowThreshold = DoubleVar()
        #self.highThreshold.set(HIGH_THRESHOLD)
        #self.lowThreshold.set(LOW_THRESHOLD)

        # define variables to use in gui elements
        self.currentTemp = StringVar()
        self.genericRelayCounter = StringVar()
        self.genericTemperatureCounter = DoubleVar()
        self.heatState = StringVar()
        self.acState = StringVar()
        self.heatStateBG = StringVar()
        self.acStateBG = StringVar()
        self.highThreshold = DoubleVar()
        self.lowThreshold = DoubleVar()
        
        #temperature thresholds
        self.highThreshold.set(HIGH_THRESHOLD)
        self.lowThreshold.set(LOW_THRESHOLD)        

        self.heatcurrentbutton = Button(self.master, textvariable=self.highThreshold, state=DISABLED, disabledforeground="black", width=3)
        self.heatcurrentbutton.place(x=250, y=75)
        self.heatButton = Button(self.master, text="HEAT", width=5, disabledforeground="black", command=self.set_heattemperature)
        self.heatButton.place(x=300, y=75)
        self.heatStateButton = Button(self.master, textvariable=self.heatState, width=10, state=DISABLED, disabledforeground="black")
        self.heatStateButton.place(x=350, y=75)

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
        tempoffset = 40.0
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

        #act on current temperature
        #if not TEST_MODE and RASPBERRY_PRESENT:
        self.temperatureAction()


    def temperatureAction(self):
        #print("temp action")
        # Gpio.gpio_active_pins = [2, 3, 8, 14, 15, 18, 23, 24]
        # temp pin assignments AC=2, HEAT=3
        temp = self.genericTemperatureCounter.get()
        if temp > HIGH_THRESHOLD and temp > LOW_THRESHOLD:
            logging.debug("Turning heat off")
            if not TEST_MODE and RASPBERRY_PRESENT:
                relayStates_2(3,0)
                relayStates_2(2,1) # Turn on AC, turn off HEAT
            self.__set_heatState("OFF")
            self.__set_acState("ON")
        elif temp < LOW_THRESHOLD and temp < HIGH_THRESHOLD:
            logging.debug("Turning heat on")
            if not TEST_MODE and RASPBERRY_PRESENT:
                relayStates_2(2,0)
                relayStates_2(3,1) # Turn on HEAT, turn off AC
            self.__set_heatState("ON")
            self.__set_acState("OFF")
        else:
            if not TEST_MODE and RASPBERRY_PRESENT:
                relayStates_2(2,0)
                relayStates_2(3,0) # Turn off HEAT, turn off AC, set to IDLE
            self.__set_heatState("IDLE")
            self.__set_acState("IDLE")
        
        self.master.after(1000, self.temperatureAction)


    def read_queues(self):
        self.genericRelayCounter.set(self.relayStates_q.get())
        #self.genericTemperatureCounter.set(self.temperatureSensor_q.get())
        self.genericTemperatureCounter.set(monitorTemperature(stop_event, temperatureSensor_q))

        # schedule to run read queues again in x milliseconds
        self.master.after(1000, self.read_queues)

    def __set_heatState(self, state):
        self.heatState.set(state)
        if state == "ON":
            self.heatStateBG.set("green")
            self.heatStateButton.configure(bg="green")
        else:
            self.heatStateBG.set("red")
            self.heatStateButton.configure(bg="red")
    
    def __set_highThreshold(self,threshold):
        pass
    
    def __set_lowThreshold(self,threshold):
        pass
    
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



'''setup 8-channel relay
change the GPIO values if the wiring changes
'''


class Gpio:
    gpio_active_pins = None

    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        Gpio.gpio_active_pins = [2, 3, 8, 14, 15, 18, 23, 24]
        for pin in Gpio.gpio_active_pins[:]:
            logging.debug("Setting up pin", pin)
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)

    def set_output(self, pin, state):
        GPIO.output(pin, state)

    def get_random_pin(self):
        return random.sample(Gpio.gpio_active_pins, 1)

    def cleanup_io(self):
        GPIO.cleanup()


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
    #monitorTemperature_t = threading.Thread(target=monitorTemperature, name="monitorTemperatureThread",
    #                                        args=[stop_event, temperatureSensor_q])

    relay_t.daemon = TRUE
    temperatureSensor_t.daemon = TRUE

    # start threads
    logging.debug("starting threads")
    relay_t.start()
    temperatureSensor_t.start()
    #monitorTemperature_t.start()

    if RASPBERRY_PRESENT:
        #don't create an instance of Gpio if the Raspberry is not present
        gp = Gpio()
    logging.debug("starting gui")
    gui = Gui(relayStates_q, temperatureSensor_q)
    gui.master.mainloop()

    #monitorTemperature_t = threading.Thread(target=monitorTemperature, name="monitorTemperatureThread",
    #                                        args=[stop_event, temperatureSensor_q, gui])

    #relay_t.join()
    #temperatureSensor_t.join()

    if 'gp' in locals():
        gp.cleanup_io()

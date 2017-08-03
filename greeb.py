#!/usr/bin/python3.4
# Copyright (c) 2017 Chris Gatehouse

RASPBERRY_PRESENT = True #TODO implement a check to see if we are actually running on a Raspberry
TEST_MODE = False

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
        logging.warning("NO RASPBERRY PRESENT")
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


'''
This is a basic test of the 8 channel relay that is connected to the Raspberry Pi. 
It sets of the GPIO and randomly cycles through the 8 channels of the relay.
This logic will be used elsewhere in Greep to control the GPIO
'''


def relayStates(stop_event, relayStates_q):
    if RASPBERRY_PRESENT:
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
        logging.warning("NO RASPBERRY PRESENT")
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
        self.currentTemp = StringVar()
        self.genericRelayCounter = StringVar()
        self.genericTemperatureCounter = StringVar()

        relayLabel = Label(self.master, textvariable=self.genericRelayCounter, width=20)
        relayLabel.place(x=150, y=150)

        temperatureLabel = Label(self.master, textvariable=self.genericTemperatureCounter, width=20)
        temperatureLabel.place(x=250, y=150)

        # start the reading the queues, self schedules after this initial run
        self.read_queues()
        # self.read_queues_fast()

    def read_queues(self):
        self.genericRelayCounter.set(self.relayStates_q.get())
        self.genericTemperatureCounter.set(self.temperatureSensor_q.get())

        # schedule to run read queues again in x milliseconds
        self.master.after(1000, self.read_queues)


'''setup 8-channel relay
change the GPIO values if the wiring changes
'''


class Gpio:
    gpio_active_pins = None

    def __init__(self):
        #self.gpio_active_pins = None
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        Gpio.gpio_active_pins = [2, 3, 8, 14, 15, 18, 23, 24]
        for pin in Gpio.gpio_active_pins[:]:
            logging.debug("Setting up pin", pin)
            GPIO.setup(pin, GPIO.OUT)

    def set_output(self, pin, state):
        GPIO.output(pin, state)

    def get_random_pin(self):
        return random.sample(Gpio.gpio_active_pins, 1)

    def cleanup_io(self):
        GPIO.cleanup()


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s')

    # create queues
    relayStates_q = LifoQueue()
    temperatureSensor_q = LifoQueue()

    # define event to stop threads
    stop_event = threading.Event()

    # define threads
    relay_t = threading.Thread(target=relayStates, name="relayThread", args=[stop_event, relayStates_q])
    temperatureSensor_t = threading.Thread(target=temperatureSensor, name="temperatureThread",
                                           args=[stop_event, temperatureSensor_q])

    relay_t.daemon = TRUE
    temperatureSensor_t.daemon = TRUE

    # start threads
    relay_t.start()
    temperatureSensor_t.start()

    if RASPBERRY_PRESENT:
        #don't create an instance of Gpio if the Raspberry is not present
        gp = Gpio()
    gui = Gui(relayStates_q, temperatureSensor_q)
    gui.master.mainloop()

    #relay_t.join()
    #temperatureSensor_t.join()

    if 'gp' in locals():
        gp.cleanup_io()

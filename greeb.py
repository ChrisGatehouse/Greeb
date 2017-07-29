#!/usr/bin/python3.4
# Copyright (c) 2017 Chris Gatehouse

RASPBERRY_PRESENT = False

from tkinter import *
import sys, os
import time, random
import threading
from queue import Queue
from queue import LifoQueue
from random import randint

# https://pypi.python.org/pypi/RPi.GPIO
if RASPBERRY_PRESENT:
    import RPi.GPIO as GPIO

'''
temperatureSensor gets the temperature from the sensor and adds the result to the queue
'''
def temperatureSensor(stop_event, temperatureSensor_q):
    if RASPBERRY_PRESENT:
        while not stop_event.wait(0):  # how often should we bother getting the temperature...
            _tempFile = open("/sys/bus/w1/devices/28-000008e0f944/w1_slave")  # TODO clean this up to work with multiple sensors
            _readFile = _tempFile.read()
            _tempFile.close()
            _data = _readFile.split("\n")[1].split(" ")[9]
            _sensorTemperature = float(_data[2:])
            _sensorTemperature = _sensorTemperature / 1000
            temperatureSensor_q.put(celsius_to_fahrenheit(_sensorTemperature))
    else:
        print("NO RASPBERRY PRESENT")
        pass

'''
This is a basic test of the 8 channel relay that is connected to the Raspberry Pi. 
It sets of the GPIO and randomly cycles through the 8 channels of the relay.
This logic will be used elsewhere in Greep to control the GPIO
'''
def relayStates(stop_event, relayStates_q):
  if RASPBERRY_PRESENT:
    GPIO.setwarnings(False)  # only here as killing from main doesn't call cleanup correctly.
    GPIO.setmode(GPIO.BCM)

    # setup 8-channel relay
    # change the GPIO values if the wiring changes
    # print("Setting up GPIO pins")
    gpio_active_pins = [2, 3, 8, 14, 15, 18, 23, 24]
    for pin in gpio_active_pins[:]:
        # print("Setting up pin", pin)
        GPIO.setup(pin, GPIO.OUT)
        i = 0
        try:
            while not stop_event.wait(.125):  # (True):
                # pick a switch at random, and turn it on/off at random
                i = i + 1  # counter for fun, just to display something to show thread is active
                pin_state = randint(0, 1)
                this_pin = random.sample(gpio_active_pins, 1)

                #  print("Setting pin " + str(this_pin) + " to state " + str(pin_state))
                GPIO.output(this_pin, pin_state)

                # one liners but broken apart above to be easier to read
                # GPIO.output(random.sample(gpio_active_pins,1),pin_state)
                # GPIO.output(random.sample(set([2,3,8,14,15,18,23,24]),1),randint(0,1))
                # GPIO.output(random.sample(gpio_active_pins,1),randint(0,1))

                # sleep for a little bit between switch, not sure how fast this switch is at the moment
                # time.sleep(.125)
                relayStates_q.put(i)
        # CTRL-C to get us out of the loop
        except (KeyboardInterrupt, SystemExit):
            pass
  else:
      print("NO RASPBERRY PRESENT")
      pass


# convert temperature in Celsius to Fahrenheit
def celsius_to_fahrenheit(celsius):
    return (celsius * 1.8) + 32


class Gui(object):
    def __init__(self,relayStates_q,temperatureSensor_q):
        # setup queues
        self.relayStates_q = relayStates_q
        self.temperatureSensor_q = temperatureSensor_q

        # setup gui window elements
        self.master = Tk()
        self.master.wm_title("Greeb in Tkinter")
        self.master.minsize(800, 480) #Official Raspberry Pi screen resolution


if __name__ == "__main__":

    #create queues
    relayStates_q = LifoQueue()
    temperatureSensor_q = LifoQueue()

    #define event to stop threads
    stop_event = threading.Event()

    #define threads
    relay_t = threading.Thread(target=relayStates, name="relayThread", args=[stop_event, relayStates_q])
    temperatureSensor_t = threading.Thread(target=temperatureSensor, name="temperatureThread",
                                 args=[stop_event, temperatureSensor_q])

    relay_t.daemon = TRUE
    temperatureSensor_t.daemon = TRUE

    #start threads
    relay_t.start()
    temperatureSensor_t.start()

    gui = Gui(relayStates_q, temperatureSensor_q)
    gui.master.mainloop()
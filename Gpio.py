#!/usr/bin/python3.4
# Copyright (c) 2017 Chris Gatehouse

# https://pypi.python.org/pypi/RPi.GPIO
import RPi.GPIO as GPIO
import logging

#These pins will change depending on the connection to the Raspberry
GPIO_ACTIVE_PINS = [2, 3, 8, 14, 15, 18, 23, 24]

'''
Gpio class addes some methods to using the RPi GPIO
this is currently setup to run 8 pins, using an 8 channel relay board
'''

class Gpio(object):
    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        for pin in GPIO_ACTIVE_PINS[:]:
            logging.debug("Setting up pin", pin)
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)

    def set_output(self, pin, state):
        GPIO.output(pin, state)

    def get_random_pin(self):
        return random.sample(GPIO_ACTIVE_PINS, 1)

    def cleanup_io(self):
        GPIO.cleanup()

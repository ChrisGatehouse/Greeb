#!/usr/bin/python3.4
#Copyright (c) 2017 Chris Gatehouse

'''
This is a basic test of the 8 channel relay that is connected to the Raspberry Pi. 
It sets of the GPIO and randomly cycles through the 8 channels of the relay.
This logic will be used elsewhere in Greep to control the GPIO
'''

import RPi.GPIO as GPIO
import time, random
from random import randint

GPIO.setmode(GPIO.BCM)

#setup 8-channel relay
#change the GPIO values if the wiring changes
print("Setting up GPIO pins")
gpio_active_pins = [2,3,8,14,15,18,23,24]
for pin in gpio_active_pins[:]:
  #print("Setting up pin", pin)
  GPIO.setup(pin, GPIO.OUT)

try:
 while(True):
  #pick a switch at random, and turn it on/off at random
  
  pin_state = randint(0,1)
  this_pin = random.sample(gpio_active_pins,1)
  
  print("Setting pin " + str(this_pin) + " to state " + str(pin_state))
  GPIO.output(this_pin,pin_state)
    
  #one liners but broken apart above to be easier to read
  #GPIO.output(random.sample(gpio_active_pins,1),pin_state)
  #GPIO.output(random.sample(set([2,3,8,14,15,18,23,24]),1),randint(0,1))
  #GPIO.output(random.sample(gpio_active_pins,1),randint(0,1))
  
  #sleep for a little bit between switch, not sure how fast this switch is at the moment
  time.sleep(.125)

#CTRL-C to get us out of the loop  
except KeyboardInterrupt:
  pass

#clean up whatever channels we have open  
GPIO.cleanup()  

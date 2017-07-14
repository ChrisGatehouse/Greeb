#!/usr/bin/python3.4
#Copyright (c) 2017 Chris Gatehouse

'''
main.py is a joining of relayTest2.py renamed to the method relayTest here. main creates a thread for relayTest
to run in while providing a main screen for the user to interact with. Functionality is limited at this point for
as it is really only to test threading and getting values back from the LifoQueue. 
'''

import RPi.GPIO as GPIO
#from multiprocessing import Queue
from queue import LifoQueue
import time, random
from random import randint
from threading import Thread
import sys, os

def main():
    print ("---- Greeb Main Menu ----")
    rt_q = LifoQueue()
    rt = Thread(target=relayTest, name="relayThread", args=[rt_q])
    rt.start()
    menu_loop = True
    #print ("To exit enter 'x'" + "\nTo see current relay count enter 'r'")
    while menu_loop:#True:
      choice = input();
      if choice == "r":
        relayCount = rt_q.get()
        print("RelayCount is", str(relayCount))
      elif choice == "x":
        menu_loop = False
        print("trying to exit...")
        rt.join()
        sys.exit(0)
      print("...")
    sys.exit(0)

'''
This is a basic test of the 8 channel relay that is connected to the Raspberry Pi. 
It sets of the GPIO and randomly cycles through the 8 channels of the relay.
This logic will be used elsewhere in Greep to control the GPIO
'''
def relayTest(rt_q):
#import RPi.GPIO as GPIO
#import time, random
#from random import randint
 GPIO.setwarnings(False) #only here as killing from main doesn't call cleanup correctly. 
 GPIO.setmode(GPIO.BCM)

#setup 8-channel relay
#change the GPIO values if the wiring changes
 #print("Setting up GPIO pins")
 gpio_active_pins = [2,3,8,14,15,18,23,24]
 for pin in gpio_active_pins[:]:
  #print("Setting up pin", pin)
  GPIO.setup(pin, GPIO.OUT)
 i = 0
 try:
  while(True):
  #pick a switch at random, and turn it on/off at random
   i = i + 1
   pin_state = randint(0,1)
   this_pin = random.sample(gpio_active_pins,1)
  
#  print("Setting pin " + str(this_pin) + " to state " + str(pin_state))
   GPIO.output(this_pin,pin_state)
    
  #one liners but broken apart above to be easier to read
  #GPIO.output(random.sample(gpio_active_pins,1),pin_state)
  #GPIO.output(random.sample(set([2,3,8,14,15,18,23,24]),1),randint(0,1))
  #GPIO.output(random.sample(gpio_active_pins,1),randint(0,1))
  
  #sleep for a little bit between switch, not sure how fast this switch is at the moment
   time.sleep(.125)
   rt_q.put(i)

#CTRL-C to get us out of the loop  
 except (KeyboardInterrupt, SystemExit):
  pass

#clean up whatever channels we have open  
GPIO.cleanup()  

if __name__=='__main__':
    main()
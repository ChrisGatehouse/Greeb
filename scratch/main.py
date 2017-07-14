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
import threading #https://docs.python.org/3/library/threading.html
import sys, os

#info on stopping threads https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread-in-python

def main():
    print ("---- Greeb Main Menu ----")
    #start thread for relay testing
    rt_q = LifoQueue() #removed maxsize for now on all queues until the best way to deal with them is found... move to DB instead?...
    pill2kill = threading.Event()
    rt = Thread(target=relayTest, name="relayThread", args=[pill2kill, rt_q])
    rt.start()
	
	#start thread for temperature sensor
    ts_q = LifoQueue()
    pill2kill_2 = threading.Event()
    ts = Thread(target=temperatureSensor, name="temperatureThread", args=[pill2kill_2, ts_q])
    ts.start()

    menu_loop = True
    print ("To exit enter 'x'" + "\nTo see current relay count enter 'r'\nTo see current temperature enter 't'")
    while menu_loop:
      choice = input();
      if choice == "r":
        relayCount = rt_q.get()
        print("RelayCount is", str(relayCount))
      elif choice == "t":
        temperature = ts_q.get()
        print("Current temperature is: {0:5.1f}F".format(temperature))# + str(temperature) + "F")
      elif choice == "x":
        menu_loop = False
        pill2kill.set() #there's a better way to do this to kill multiple threads at once with on pill, look that up.
                        #https://stackoverflow.com/questions/18018033/how-to-stop-a-looping-thread-in-python		
        pill2kill_2.set()
        rt.join()
        ts.join()
        GPIO.cleanup()

'''
This is a basic test of the 8 channel relay that is connected to the Raspberry Pi. 
It sets of the GPIO and randomly cycles through the 8 channels of the relay.
This logic will be used elsewhere in Greep to control the GPIO
'''
def relayTest(stop_event, rt_q):
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
  while not stop_event.wait(.125):#(True):
  #pick a switch at random, and turn it on/off at random
   i = i + 1 #counter for fun, just to display something to show thread is active
   pin_state = randint(0,1)
   this_pin = random.sample(gpio_active_pins,1)
  
#  print("Setting pin " + str(this_pin) + " to state " + str(pin_state))
   GPIO.output(this_pin,pin_state)
    
  #one liners but broken apart above to be easier to read
  #GPIO.output(random.sample(gpio_active_pins,1),pin_state)
  #GPIO.output(random.sample(set([2,3,8,14,15,18,23,24]),1),randint(0,1))
  #GPIO.output(random.sample(gpio_active_pins,1),randint(0,1))
  
  #sleep for a little bit between switch, not sure how fast this switch is at the moment
   #time.sleep(.125)
   rt_q.put(i)

#CTRL-C to get us out of the loop  
 except (KeyboardInterrupt, SystemExit):
  pass

#clean up whatever channels we have open  
#GPIO.cleanup()  

'''
The temperatureSensor method reads the temperature from the DS18B20 sensor, currently only written for one sensor reading
'''
def temperatureSensor(stop_event, ts_q):
  while not stop_event.wait(0): #how often should we bother getting the temperature...
    _tempFile = open("/sys/bus/w1/devices/28-000008e0f944/w1_slave") #TODO clean this up to work with multiple sensors
    _readFile = _tempFile.read()
    _tempFile.close()
    _data = _readFile.split("\n")[1].split(" ")[9]
    _sensorTemperature = float(_data[2:])
    _sensorTemperature = _sensorTemperature / 1000
    ts_q.put(CtoFconversion(_sensorTemperature))

#convert temperature in Celsius to Fahrenheit
def CtoFconversion(InC):
  return((InC * 1.8) + 32)
	
if __name__=='__main__':
    main()
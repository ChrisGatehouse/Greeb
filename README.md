# Greeb

Copyright © 2017 Chris Gatehouse

Greeb is a home automation suite powered by the Raspberry Pi.
It is intended to easlily run any device that can either be physically connected the pi or connected through a network i.e. the internet or home. Interaction is done through the devices API if one is available otherwise another method will be devised.

This project is written in Python3, and is a continuous work in progress. Python3 was chosen as it has many libraries availble or the Raspberry and also documentation to allow for easy implementation of new features. It was also chosen as a learning expierence to force my learning of the Python language. 

# Motivation
I have seen many differnt home automation systems. The problem is commericial systems are always lacking in some feature that you want either because it doesn't fit in their ecosystem or it is outside of their scope. Other open source projects seem to die off quickly or are only addressing specific problem areas.

# Week 3 Project Status
Parts have arrived and making progress on connecting and using the hardware with the Pi. 
Working on the menu system of Greeb, the intent is to have a forward facing menu running in Python for now while all logic, hardware and sensors run in background threads.
Menu currently works only with the relay switch and while it correctly gets values from the threads queue it has trouble exiting.
The next thread that will be started is the temperature sensor and hopefully have that tied in to controlling relay actions soon.

# Build Instructions / Installation
This is intended to be used with minimal setup of the software, below is what you'll need to get started.
1. Raspbery Pi 2 or 3 (tested with Raspberry Pi 3)
2. Latest update of Raspian OS
3. Python3.4
4. An 8-channel 5V DC relay (tested with http://a.co/0LYsu2P)
5. A DS18B20 temperature sensor. Setup is needed to enable on the Pi there are instructions here: http://www.circuitbasics.com/raspberry-pi-ds18b20-temperature-sensor-tutorial/
6. A power supply to power any device you need to off of the relay board, otherwise you will connect it to your HVAC relay leads

# Planned features
This is a list of features that currently don't exist or enhancements to existing features

-Move the data that is currently stored in queues to a database (enhancement)

-Learning algoritm to predict heating and cooling times during the day (new)

-Automation based on external conditions i.e. HVAC based on weather, lighting based on time (new)

-Wemo device control either custom implementation or use https://github.com/iancmcc/ouimeaux (new)

# Known issues
-Setting a Heat value higher then current temperature and an AC value higher than current temperature sets the system to IDLE the display is misleading

-TEST_MODE is no longer working correctly

-The current temperature is updated too frequently

-The current implementation of the temperature sensor only handles one sensor and setup is manual

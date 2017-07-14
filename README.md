# Greeb
Greeb is a home automation suite powered by the Raspberry Pi 
It is intended to easlily run any device that can either be physically connected the pi or connected through a network. Interaction is done through the devices API if one is available otherwise another method will be devised.

# Motivation
I have seen many differnt home automation systems. The problem is commericial systems are always lacking in some feature that you want either because it doesn't fit in their ecosystem or it is outside of their scope. Other open source projects seem to die off quickly or are only addressing specific problem areas.

# Week 3 Project Status
Parts have arrived and making progress on connecting and using the hardware with the Pi. 
Working on the menu system of Greeb, the intent is to have a forward facing menu running in Python for now while all logic, hardware and sensors run in background threads.
Menu currently works only with the relay switch and while it correctly gets values from the threads queue it has trouble exiting.
The next thread that will be started is the temperature sensor and hopefully have that tied in to controlling relay actions soon.

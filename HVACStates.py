#!/usr/bin/python3.4
# Copyright (c) 2017 Chris Gatehouse

from enum import Enum

'''
States is to define the states exist for the HVAC
'''

class HVACStates(Enum):
    IDLE = 0
    OFF = 1
    ON = 2
    MANUAL = 3
    AUTO = 4


# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 13:47:49 2019

@author: cmiller
"""

from pyduino import *
import time

if __name__ == '__main__':
    
    a = Arduino()

    time.sleep(3)
    # sleep to ensure ample time for computer to make serial connection 

    PIN = 52
    a.set_pin_mode(PIN,'O')
    # initialize the digital pin as output

    time.sleep(1)
    # allow time to make connection

    a.digital_write(PIN,1) # turn LED on 
    time.sleep(1)
    a.digital_write(PIN,0) # turn LED off
    time.sleep(1)
    a.close()

# -*- coding: utf-8 -*-
"""
Read data from DATAQ DI-245.
See DI-245 Communication Protocol:
    https://www.dataq.com/resources/pdfs/support_articles/DI-245-protocol.pdf
    
TODO: Make sure program is consistent.  Why: invalid literal for int() with base 16: 'X'
    #See https://stackoverflow.com/questions/13120437/base-16-error-in-an-hex-transformation-function-with-python
TODO: Make sure sample size is correct

"""

import dataq
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
from serial import SerialException
from time import sleep

SAMPLE_PERIOD=5 #seconds
TIME_DELAY=1 #seconds
SAMPLE_RATE=200 #Hz
FULL_SCALE_RANGE=0.5 #0.5 seems to work well
TEST_CURRENT=0.8 #Amps
NOISE_DATA_FOLDER=r'C:\Users\cmiller\Desktop\Noise'

#Define list of pins to control
pins=[3,5,7]

#Set Pin Numbering mode
GPIO.setmode(GPIO.BOARD)
#Define control states
off=GPIO.HIGH
on=GPIO.LOW
#Setup pins & set initial state
GPIO.setup(pins, GPIO.OUT)
GPIO.output(pins,GPIO.HIGH)

#Initialize connection to DATAQ
try:
    #Initialize connection to DATAQ
    ser=dataq.connect()
    sleep(1)
    #Flush input buffer
    ser.reset_input_buffer()    
    #Populate scan list
    dataq.populate_scan_list(ser,FULL_SCALE_RANGE)
    sleep(1)
    #Set sample rate
    dataq.set_sample_rate(ser)
    sleep(1)
    #Send "Start Scan" (S1) ASCII command
    ser.write(bytes(b'S1'))
    
    for idx, _ in enumerate(pins):
        #Turn pin on for sample period, then off
        GPIO.output(pins[idx],on)
        sleep(SAMPLE_PERIOD)
        GPIO.output(pins[idx],off)
        #Read data
        voltage, time=dataq.read_data(ser,FULL_SCALE_RANGE,SAMPLE_RATE,SAMPLE_PERIOD)  
        #Print & Plot Results
        print('Sample Rate: ' + str(len(voltage)/SAMPLE_PERIOD) + ' Hz')
        print('Noise: ' + str(round((max(voltage)-min(voltage))/TEST_CURRENT,4)) + '  Ω')
        plt.plot(time, voltage); plt.xlabel('Time (s)'); plt.ylabel('Voltage (V)');
        #Save results
        dataq.save_to_text(time, voltage, NOISE_DATA_FOLDER, idx)
        sleep(TIME_DELAY) 
except SerialException:
    print("Failed to connect to DATAQ")
    GPIO.cleanup()
except KeyboardInterrupt:
    print("Program Exit: Keyboard Interrupt")
    GPIO.cleanup()
finally:
    GPIO.cleanup()
    #Send "Stop Scan" S0 ASCII command
    ser.write(bytes(b'S0'))
    ser.close()

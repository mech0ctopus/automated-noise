# -*- coding: utf-8 -*-
"""
Read data from DATAQ DI-245.
See DI-245 Communication Protocol:
    https://www.dataq.com/resources/pdfs/support_articles/DI-245-protocol.pdf
    
TODO: Write data to text file.
    #https://stackoverflow.com/questions/899103/writing-a-list-to-a-file-with-python
TODO: Make sure program is consistent.  Why: invalid literal for int() with base 16: 'X'

"""

from time import sleep
import matplotlib.pyplot as plt
import dataq

SAMPLE_PERIOD=1 #seconds
SAMPLE_RATE=200 #Hz
FULL_SCALE_RANGE=0.5
TEST_CURRENT=0.8 #Amps
CHANNEL_NUMBER=1

try:
    #Initialize connection to DATAQ
    ser=dataq.connect()
    sleep(1)
except:
    print('Failed to connect to DATAQ')

try:
    #Flush input buffer
    ser.reset_input_buffer()    
    #Populate scan list
    dataq.populate_scan_list(ser,FULL_SCALE_RANGE)
    sleep(1)
    #Set sample rate
    dataq.set_sample_rate(ser)
    sleep(1)
    #Send "Start Scan" (S1) ASCII command
    ser.write(b'S1')
    sleep(SAMPLE_PERIOD)
    #Read data
    voltage, time=dataq.read_data(ser,FULL_SCALE_RANGE,SAMPLE_RATE,SAMPLE_PERIOD)  
    #Print & Plot Results
    print('Sample Rate: ' + str(len(voltage)) + ' Hz')
    print('Noise: ' + str(round((max(voltage)-min(voltage))/TEST_CURRENT,4)) + '  Ω')
    plt.plot(time, voltage); plt.xlabel('Time (s)'); plt.ylabel('Voltage (V)');
    #Save results
    dataq.save_to_text(voltage, r'C:\Users\cmiller\Documents\GitHub\automated-noise',CHANNEL_NUMBER)
    
except KeyboardInterrupt:
    print("Program Exit: Keyboard Interrupt")
finally:
    #Send "Stop Scan" S0 ASCII command
    ser.write(b'S0')
    ser.close()
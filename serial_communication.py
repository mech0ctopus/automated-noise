# -*- coding: utf-8 -*-
"""
Read data from DATAQ DI-245.

TODO: Write data to text file.
TODO: Determine if data is being held up at serial port.  
      Are we just reading Channel 1?
"""

import serial
import time

#Sample time in seconds
SAMPLE_PERIOD=1

def fsr_to_voltage(counts, fsr):
    '''Converts full-scale range and ADC counts to voltage'''
    voltage=fsr*counts/8192
    return voltage

#Setup serial connection per DI-245 Communication Protocol documentation
ser = serial.Serial(port="COM4",
                    baudrate=115200,
                    bytesize=serial.EIGHTBITS,
                    stopbits=serial.STOPBITS_ONE,
                    parity=serial.PARITY_NONE,
                    timeout=1)

time.sleep(1)

try:
    #Populate Scan List
    #Enable Channel 0 for ±5V range as first scan list member
    #Analog in, CHannel 0, Mode=0, Range=1, ±5V, FSR=011
    #Define value: 0000101100000000=2816 (bin=dec)
    ser.write(b'chn 0 2816')
    time.sleep(1)
    #Set sample rate for one channel to 200 Hz
    #xrate=200, burst sample rate per channel = 200Hz
    #SF=8000/200-1=39.  SF=111001
    #Sinc4=0
    #AF=0
    #B=200. B=0000
    ser.write(b'xrate 57 200')
    time.sleep(1)
    #Send "Start Scan" (S1) ASCII command
    ser.write(b'S1')
    print('Command Sent to DATAQ')

    time.sleep(SAMPLE_PERIOD)
    
    print("DATAQ Response:")
    
    #Check number of bytes in input buffer
    if ser.in_waiting>0:
        print('In Waiting: ' + str(ser.in_waiting))
        data=ser.read(ser.in_waiting)
        print(data)
    
        #Create list of sample data
        data=str(data)
        data=data.strip("b'S1t")
        hex_data=data.split('\\x')
        #Remove empty strings from list
        hex_data=list(filter(None,hex_data))
        print(hex_data)
    
        #Convert data to int16
        int_data=[int(sample,16) for sample in hex_data]
        print(int_data)
        
        #Convert to voltage
        v=[fsr_to_voltage(sample,5) for sample in int_data]
        print(v)
        
        #Open:4.962V, Short: 0.112V
    
except KeyboardInterrupt:
    print("Program Exit: Keyboard Interrupt")
finally:
    #Send "Stop Scan" S0 ASCII command
    ser.write(b'S0')
    ser.close()
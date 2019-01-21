# -*- coding: utf-8 -*-
"""
Read data from DATAQ DI-245.
See DI-245 Communication Protocol:
    https://www.dataq.com/resources/pdfs/support_articles/DI-245-protocol.pdf
    
TODO: Write data to text file.
TODO: Make sure program is consistent
TODO: Clean up code.  Abstract into functions where possible.

"""

import serial
import time
import re
import matplotlib.pyplot as plt
from numpy import linspace

#Sample time in seconds
SAMPLE_PERIOD=1
#Define sample rate (Hz)
SAMPLE_RATE=200
#Full Scale Range for Voltage.
FULL_SCALE_RANGE=0.5

def fsr_to_voltage(counts, fsr):
    '''Converts full-scale range and ADC counts to voltage'''
    voltage=fsr*counts/8192
    return voltage

def save_to_text(data, filepath, channel_number):
    '''Saves voltage readings to text file'''
    f=open(filepath + '//' + str(channel_number) +'.txt.',mode='w')
    f.write(data)
    f.close()

def connect(port='COM4'):
    '''Setup serial connection per DI-245 Communication Protocol documentation'''
    ser = serial.Serial(port=port,
                        baudrate=115200,
                        bytesize=serial.EIGHTBITS,
                        stopbits=serial.STOPBITS_ONE,
                        parity=serial.PARITY_NONE,
                        timeout=1)
    return ser

ser=connect()

time.sleep(1)

try:
    #Flush input buffer
    ser.reset_input_buffer()    
    
    #Populate Scan List
    #Enable channel based on FSR
    if FULL_SCALE_RANGE==5:
        #Enable Channel 0 for ±5V range as first scan list member
        #Analog in, Channel 0, Mode=0, Range=1, ±5V, FSR=011
        #Define value: 0000101100000000=2816 (bin=dec)
        ser.write(b'chn 0 2816')
    elif FULL_SCALE_RANGE==1:
        #Enable Channel 0 for ±1V range as first scan list member
        #Analog in, Channel 0, Mode=0, Range=1, ±1V, FSR=101
        #Define value: 0000110100000000=3328 (bin=dec)
        ser.write(b'chn 0 3328')
    elif FULL_SCALE_RANGE==0.5:
        #Enable Channel 0 for ±500mV range as first scan list member
        #Analog in, Channel 0, Mode=0, Range=0, ±500mV, FSR=000
        #Define value: 0000000000000000=0 (bin=dec)
        ser.write(b'chn 0 0')
    else:
        raise("Undefined FSR")
    
    time.sleep(1)
    #Set sample rate for one channel to 200 Hz
    #xrate=200, burst sample rate per channel = 200Hz
    #SF=8000/200-1=39.  SF=111001, Sinc4=0, AF=0, B=200. B=0000
    ser.write(b'xrate 57 200')
    time.sleep(1)
    #Send "Start Scan" (S1) ASCII command
    ser.write(b'S1')

    time.sleep(SAMPLE_PERIOD)

    #Check number of bytes in input buffer
    if ser.in_waiting>0:
        #Response is continuous binary stream of 1x 16 bit (2x bytes) words per measurement.
        #Add 2 for the characters that are filtered out
        #print('Bytes In Waiting: ' + str(ser.in_waiting))
        #print('Bits In Waiting: ' + str(ser.in_waiting*8))
        data=ser.read(2*SAMPLE_RATE*SAMPLE_PERIOD+2)

        #Create string of sample data
        data=str(data)[4:-1]

        #Remove unwanted characters
        re.sub('[^A-Za-z0-9]+', '',data)
        #Parse string of sample data into list
        hex_data=data.split('\\x')
        #Remove empty strings from list
        hex_data=list(filter(None,hex_data))
        #Convert data to int16
        int_data=[int(sample,16) for sample in hex_data]
        bin_data=[bin(sample)[2:] for sample in int_data]

        #Analog channel coding (p.10)
        #Read 16 bits & Create words
        words=[]
        if (len(bin_data)) % 2==0:
            #even
            length=int(len(bin_data)/2)
        else:
            #odd
            length=int((len(bin_data)-1)/2)
            
        for i in range(length):
            #Byte 2 + Byte 1 (p.10), Remove sync bit
            words.append(bin_data[2*i+1][0:7]+bin_data[2*i][0:7])
            
            #Invert MSB of word.  MSB:= the bit of highest numerical value
            if words[i][0]=='1':
                words[i]=words[i].replace('1','0',1)
            elif words[i][0]=='0':
                words[i]=words[i].replace('0','1',1)
            else:
                raise('Non-binary entry in word.')

        #Sync with stream based on position of B0 (Find starting point)
        
        #Convert words to adc_counts (Treat as twos complement number)
        adc_counts=[int(word,2) for word in words]
        
        #Convert to voltage
        voltage=[fsr_to_voltage(adc_count,FULL_SCALE_RANGE) for adc_count in adc_counts]
        voltage=[round(sample,4) for sample in voltage]
        time=linspace(0,SAMPLE_PERIOD,num=SAMPLE_RATE*SAMPLE_PERIOD)
        
        #Print & Plot Results
        print('Number of Samples: ' + str(len(voltage)))
        print('Noise: ' + str(round((max(voltage)-min(voltage))/0.8,4)))
        plt.plot(time, voltage); plt.xlabel('Time (s)'); plt.ylabel('Voltage (V)');
    
except KeyboardInterrupt:
    print("Program Exit: Keyboard Interrupt")
finally:
    #Send "Stop Scan" S0 ASCII command
    ser.write(b'S0')
    ser.close()
# -*- coding: utf-8 -*-
"""
DATAQ DI-245 Functions
"""
import serial
from re import sub
from numpy import linspace
import struct
from bitstring import BitArray

def fsr_to_voltage(counts, fsr):
    '''Converts full-scale range and ADC counts to voltage'''
    voltage=fsr*counts/8192
    return voltage

def save_to_text(xdata, ydata, filepath, channel_number):
    '''Saves voltage readings & time to text file'''
    with open(str(channel_number)+'.txt', 'w') as f:
        for x,y in zip(xdata,ydata):
            f.write(str(x)+','+str(y)+",\n")

def connect(port='COM4'):
    '''Setup serial connection per DI-245 Communication Protocol documentation'''
    ser = serial.Serial(port=port,
                        baudrate=115200,
                        bytesize=serial.EIGHTBITS,
                        stopbits=serial.STOPBITS_ONE,
                        parity=serial.PARITY_NONE,
                        timeout=1)
    return ser

def populate_scan_list(ser, fsr):
    '''Populate Scan List'''
    #Enable channel based on FSR
    if fsr==5:
        #Enable Channel 0 for ±5V range as first scan list member
        #Analog in, Channel 0, Mode=0, Range=1, ±5V, FSR=011
        #Define value: 0000101100000000=2816 (bin=dec)
        ser.write(b'chn 0 2816')
    elif fsr==1:
        #Enable Channel 0 for ±1V range as first scan list member
        #Analog in, Channel 0, Mode=0, Range=1, ±1V, FSR=101
        #Define value: 0000110100000000=3328 (bin=dec)
        ser.write(b'chn 0 3328')
    elif fsr==0.5:
        #Enable Channel 0 for ±500mV range as first scan list member
        #Analog in, Channel 0, Mode=0, Range=0, ±500mV, FSR=000
        #Define value: 0000000000000000=0 (bin=dec)
        ser.write(b'chn 0 0')
    else:
        raise("Undefined FSR")

def read_data(ser,fsr,sample_rate,sample_period):
    #Check number of bytes in input buffer
    if ser.in_waiting>0:
        #Response is continuous binary stream of 1x 16 bit (2x bytes) words per measurement.
        #Add 2 for the characters that are filtered out
        data_list=[]
        data=[]
        for _ in range(sample_rate*sample_period+1):
            byte_pair=ser.read(2)
            struct.unpack('h',byte_pair)
            data_list.append(str(byte_pair)[2:])
        for item in data_list:
            sub('[^A-Za-z0-9]+', '',item)
            parsed_items=item.split('\\x') 

            for parsed_item in parsed_items:
                parsed_item=parsed_item.replace('"','')
                parsed_item=parsed_item.replace("'",'')
                if parsed_item != '':
                    data.append(parsed_item)
                
        #Remove first entry
        data=data[1:]
        data==list(filter(None,data))
        
        print(data)
        
        #Convert data to int16, then binary
        bin_data=[bin(int(sample,16))[2:] for sample in data]
        
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
        voltage=[fsr_to_voltage(adc_count,fsr) for adc_count in adc_counts]
        voltage=[round(sample,4) for sample in voltage]
        time=linspace(0,sample_period,num=sample_rate*sample_period)
        print(voltage)
        return voltage, time
        
def set_sample_rate(ser):
    '''Set sample rate for one channel to 200 Hz'''
    #xrate=200, burst sample rate per channel = 200Hz
    #SF=8000/200-1=39.  SF=111001, Sinc4=0, AF=0, B=200. B=0000
    ser.write(b'xrate 57 200')
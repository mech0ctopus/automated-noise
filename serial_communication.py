# -*- coding: utf-8 -*-
"""
Read data from DATAQ DI-245.

TODO: Write data to text file.
TODO: Troubleshoot why code never reads incoming data
TODO: Determine if data is being held up at serial port.  
      Are we just reading Channel 1?
"""

import serial
import time

SAMPLE_PERIOD=1

#Setup serial connection per DI-245 Communication Protocol documentation
ser = serial.Serial(port="COM4",
                    baudrate=115200,
                    bytesize=serial.EIGHTBITS,
                    stopbits=serial.STOPBITS_ONE,
                    parity=serial.PARITY_NONE,
                    timeout=1)

time.sleep(1)

#Send test "A1" ASCII command
try:
    ser.write(b'S1')
    print("S1 Command Sent to DATAQ")

    time.sleep(SAMPLE_PERIOD)
    
    print("DATAQ Response:")
    
    #Check number of bytes in input buffer
    if ser.in_waiting>0:
        print('In Waiting: ' + str(ser.in_waiting))
        data=ser.read(ser.in_waiting)
        print(data)
    
    #Create list of sample data
    data=str(data)
    hex_data=data.split('\\x')
    print(hex_data)
    
    #Convert data to int16
    int_data=[int(sample,16) for sample in hex_data]
    print(int_data)
    
except KeyboardInterrupt:
    print("Program Exit: Keyboard Interrupt")
finally:
    #Send "Stop Scan" S0 ASCII command
    print("Finally")
    ser.write(b'S0')
    ser.close()
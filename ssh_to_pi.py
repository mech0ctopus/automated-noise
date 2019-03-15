# -*- coding: utf-8 -*-
"""
Send commands to RPi over local network

Must be on the same WiFi network as RPi.
"""

import paramiko
from time import sleep

commands=['python3 /home/pi/Desktop/automated-noise/relay_control.py']

# Initialize SSH connection
ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Connect to Pi over local network
    ssh.connect("10.1.11.68",username="pi",password="raspberry")
    print('Successfully Connected')
except:
    print("Attempt to Connect Failed")
    
for cmd in commands:
    # Send command to Pi
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
    # Print response from Pi
    print(ssh_stdout.read())
    ssh_stdin.flush()
    sleep(2)
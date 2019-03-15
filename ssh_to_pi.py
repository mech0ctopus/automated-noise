# -*- coding: utf-8 -*-
"""
Send commands to RPi over local network

Must be on the same WiFi network as RPi.
"""

import paramiko

CMD='ls'

# Initialize SSH connection
ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Connect to Pi over local network
    ssh.connect("10.1.11.68",username="pi",password="raspberry")
except:
    print("Attempt to Connect Failed")
    
# Send command to Pi
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(CMD)

# Print response from Pi
print(ssh_stdout.read())
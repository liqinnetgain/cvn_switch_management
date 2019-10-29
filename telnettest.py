import telnetlib
import re
import sys
import time
import os

ip = "10.11.104.2"
username = "root"
password = "mduadmin"
TELNET_PORT = 23
TELNET_TIMEOUT = 5
READ_TIMEOUT = 5
# Logging into device (logging in to intermediate device (Fortigate) first)
print("------------------------------------------------------------------------------")
print("Started logging into Switch %s" % ip)
connection = telnetlib.Telnet(ip, TELNET_PORT, TELNET_TIMEOUT)
time.sleep(3)
# Entering global config mode
connection.write((username + "\n").encode('ascii'))
time.sleep(3)
connection.write((password + "\n \r").encode('ascii'))
time.sleep(3)
connection.write("enable\n".encode('ascii'))
connection.write("config\n".encode('ascii'))
time.sleep(2)
connection.write("mmi-mode original-output\n".encode('ascii'))
time.sleep(2)
connection.write("quit\n".encode('ascii'))
connection.write("display current-configuration\n \r".encode('ascii'))
print("wait for a while depend on the length of configuration file")
time.sleep(10)
output = connection.read_very_eager()
print ("Write configuration to text file")
newfile = open('mdu', "wb")
# output = output.split("display current-configuration".encode())[1]
newfile.write(output)
newfile.close
connection.write("quit\ny".encode('ascii'))
time.sleep(2)
# Closing the connection
connection.close()

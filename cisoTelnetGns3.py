# https://github.com/sohag1426/ciscoTelnetPython/blob/master/ciscoTelnetGns3.py
import datetime
import os
import subprocess
import telnetlib
import time

username = "root"
unamepw = "mduadmin"
ip = "10.11.104.2"

tn = telnetlib.Telnet(ip)
time.sleep(2)
response = tn.read_until(b":", 5)
print(response)

if b"User name" in response:
    print("found")
    tn.write(username.encode('ascii') + b"\n")
    output = tn.read_until(b":", 5)
    print(output)
    tn.write(unamepw.encode('ascii') + b"\n \r")
    output = tn.read_until(b">", 5)
    # tn.write(b" " + b"\n")
    print(output)
    tn.write(b"enable" + b"\n")
    output = tn.read_until(b":", 5)
    print(output)
    tn.write(b"display version" + b"\n\n")
    tn.write(b" " + b"\n\n")
    output = tn.read_until(b"#", 5)
    print(output)
else:
    print("not found")
tn.write(b"display version" + b"\n\n")
output = tn.read_until(b"#", 5)
print(output)

# tn.write(b"show vlan" + b"\n")
# output = tn.read_until(b"#", 5)
# print(output)
'''
tn.write(b"configure terminal" + b"\n")
output = tn.read_until(b"#", 5)
print(output)

tn.write(b"vlan 222" + b"\n")
output = tn.read_until(b"#", 5)
print(output)

tn.write(b"end" + b"\n")
output = tn.read_until(b"#", 5)
print(output)

tn.write(b"show vlan" + b"\n")
output = tn.read_until(b"#", 5)
print(output)
'''
tn.close()



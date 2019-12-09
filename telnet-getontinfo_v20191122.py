#!/usr/bin/python
import calendar
import datetime
import os
import subprocess
import telnetlib
import time

debug = True
username = "root"
unamepw = "ESPL888espl"
ipv4 = "10.12.97.5"
isTest = False


def host_is_up(ipv4):
    if isTest:
        print ("host_is_up in test mode")
        return True
    # Check ping to host, if host is up response will be 0
    print("------------------------------------------------------------------------------")
    print("Check the availability of device %s" % ipv4)
    response = os.system("ping -c 2 " + ipv4)
    if response == 0:
        a = ipv4.split(".")
        return (len(a) == 4) and (1 <= int(a[0]) <= 255) and (0 <= int(a[1]) <= 255) and (0 <= int(a[2]) <= 255) and (
                0 <= int(a[3]) <= 255)
    else:
        return False


def get_ont_optics():
    if isTest:
        print ("get_ont_optics in test mode. return mock data")
        return
    fn = "optics"
    tn = telnetlib.Telnet(ipv4)
    # time.sleep(5)
    # response = tn.read_until(b":", 5)
    tn.read_until(b":", 5)
    tn.write(username.encode('ascii') + b"\n")
    tn.read_until(b":", 5)
    tn.write(unamepw.encode('ascii') + b"\n")
    tn.write(b" \n")
    print("------------------------------------------------------------------------------")
    print("Started logging into Switch %s" % ipv4)
    # time.sleep(0.5)
    # tn.read_until(b">", 5)
    # tn.write(b" " + b"\n")
    tn.write(b"enable" + b"\n")
    tn.write(b"scroll" + b"\n")
    tn.read_until(b":", 5)
    tn.write(b"" + b"\n")
    time.sleep(0.5)

    tn.write("display ont\n".encode('ascii'))
    time.sleep(0.5)
    tn.write("info\n".encode('ascii'))
    time.sleep(0.5)
    tn.write("summary 0\n".encode('ascii'))
    time.sleep(0.5)
    tn.write("0\n".encode('ascii'))
    time.sleep(10)
    output = tn.read_very_eager()
    # Write configuration to text file
    ts = calendar.timegm(time.gmtime())
    filename = fn + str(ts) + ".txt"
    newfile = open(filename, "wb")
    #print output
    newfile.write(''.join(output))
    newfile.close
    print("Saved optic powers to the file")
    print("------------------------------------------------------------------------------")
    tn.write("exit\n".encode('ascii'))
    # time.sleep(2)

    tn.close()


def get_ont_optics_loop():
    mins = 240
    mins = 60
    interval = 60 * mins  # 60 * 60 * 5 =5 min  60 * 60  = 1 hour,

    get_ont_optics()

    tm = time.time() + interval
    while True:
        if time.time() <= tm:
            print ("waiting for a while ... " + str(datetime.datetime.now()))
            time.sleep(60 * float( mins/3))
            continue
            
        get_ont_optics()
        tm = time.time() + interval
        print ("Next ont info checking will be in " + str(mins) + " minutes later at " + str(tm))
    return


if __name__ == '__main__':

    if host_is_up(ipv4):
        # get_ont_optics()
        get_ont_optics_loop()
    else:
        print("This ip address %s is invalid or not available" % ipv4)
        print("------------------------------------------------------------------------------")


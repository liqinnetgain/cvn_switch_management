# -*- coding: utf-8 -*-
import telnetlib
import time
import os

hostname = "global"


def disable_paging(connection):
    # Disable paging on a Cisco router
    connection.write("config\n".encode('ascii'))
    connection.write("mmi-mode original-output\n\r".encode('ascii'))
    connection.write("".encode('ascii'))
    time.sleep(0.1)
    connection.write("quit\r".encode('ascii'))
    return


def host_is_up(ipv4):
    # Check ping to host, if host is up response will be 0
    print("------------------------------------------------------------------------------")
    print("Check the availability of device %s" % ipv4)
    response = os.system("ping -n 2 " + ipv4)
    return response == 0


def check_ipv4_validity(ip_address):
    a = ip_address.split(".")
    return (len(a) == 4) and (1 <= int(a[0]) <= 255) and (0 <= int(a[1]) <= 255) and (0 <= int(a[2]) <= 255) and (
            0 <= int(a[3]) <= 255)


def get_config(ip, username, password):
    # This function will telnet to device to get configuration by show running-config
    try:
        TELNET_PORT = 23
        TELNET_TIMEOUT = 5
        # Logging into device (logging in to intermediate device (Fortigate) first)
        print("------------------------------------------------------------------------------")
        print("Started logging into Switch %s" % ip)
        connection = telnetlib.Telnet(ip, TELNET_PORT, TELNET_TIMEOUT)
        time.sleep(1)
        connection.write((username + "\n").encode('ascii'))
        time.sleep(1)
        connection.write((password + "\r\n").encode('ascii'))
        time.sleep(3)
        # Entering global config mode
        connection.write("enable\n".encode('ascii'))
        disable_paging(connection)
        connection.write("display current-configuration\n\n".encode('ascii'))
        # depend on the length of configuration file
        time.sleep(10)
        output = connection.read_very_eager()
        # Write configuration to text file
        newfile = open(hostname + '.txt', "wb")
        # output split not working?
        # output = output.split("display current-configuration".encode()[1])
        # print (''.join(output))
        newfile.write(''.join(output))
        newfile.close
        print("Saved configuration file of device %s" % hostname)
        print("------------------------------------------------------------------------------")
        connection.write("exit\n".encode('ascii'))
        time.sleep(2)
        # Closing the connection
        connection.close()

    except IOError:
        print ("Input parameter error! Please check username, password and file name.")


# Define the input file, including ip, username and password file
switch_file = "sw_cvn_tl.txt"
# Open switch selected file for reading
selected_switch_file = open(switch_file, 'r')

# Starting from the beginning of the file
selected_switch_file.seek(0)

# Switch file must is as below: ip username password, for ex:
# 192.168.1.10 admin password
for each_line in selected_switch_file.readlines():
    temp = each_line.split(" ")
    hostname = temp[0]
    ipv4 = temp[1]
    username = temp[2]
    password = temp[3].rstrip("\n")

    print('hostname is', hostname)
    print('IP is', ipv4)
    print('Username is', username)
    print('Password is', password)

    if check_ipv4_validity(ipv4) and host_is_up(ipv4):
        get_config(ipv4, username, password)
    else:
        print("This ip address %s is invalid or not available" % ipv4)
        print("------------------------------------------------------------------------------")

# Closing the switch file
selected_switch_file.close()

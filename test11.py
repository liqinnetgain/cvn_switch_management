#!/usr/bin/env python
# -*- coding:utf-8 -*-

from multiprocessing import Process, Pool
import time
import paramiko
import sys
import os

host_list = (
    ('10.11.104.5', 'liqin', 'lq', 'df -Th'),
    ('10.11.104.2', 'root', 'mduadmin', 'display version')
)

s = paramiko.SSHClient()
s.load_system_host_keys()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())


def ssh_run(host_info):
    ip, username, password, cmd = host_info
    s.connect(ip, 22, username, password, timeout=5)
    stdin, stdout, stderr = s.exec_command(cmd)
    cmd_result = stdout.read(), stderr.read()
    print ('\033[32;1m----------------%s------------------\033[0m' % ip)
    for line in cmd_result:
        print (line)


p = Pool(processes=1)
result_list = []

for h in host_list:
    result_list.append(p.apply_async(ssh_run, [h, ]))

for res in result_list:
    res.get()

s.close()

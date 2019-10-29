#!/usr/bin/env python
# -*- coding:utf-8 -*-
import paramiko
from multiprocessing import Process, Pool
import time

host_list = (
    ('10.174.85.167', 'root', '123456'),
    ('139.16.139.15', 'root', '123456'),
    ('139.24.11.58', 'root', '666448')
)

s = paramiko.SSHClient()
s.load_system_host_keys()  # 加载本机.ssh/knows_host文件
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def ssh_run(host_info, cmd):
    ip, username, password = host_info
    s.connect(ip, 22, username, password, timeout=5)
    stdin, stdout, stderr = s.exec_command(cmd)
    cmd_result = stdout.read(), stderr.read()
    print ('\033[32;1m----------------%s------------------\033[0m' % ip)
    for line in cmd_result:
        print (line)


p = Pool(processes=2)
result_list = []
q = 'quit'
e = 'exit'

# ------通过输入来判断------

while True:
    input_cmd = input("please input command:").strip()
    if input_cmd == q or input_cmd == e:
        break
    else:
        for h in host_list:
            result_list.append(p.apply_async(ssh_run, [h, input_cmd]))

        for res in result_list:
            res.get()
s.close()

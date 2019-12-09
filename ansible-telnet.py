#!/usr/bin/env python2.7
# encoding: utf-8

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = """
    author: Zhong Dong Yue <zhongdongyue@gmail.com>
    connection: telnet
    short_description: Allow ansible to piggyback on telnet
    description:
        - This allows you to use existing telnet infrastructure to connect to targets.
    version_added: "1.0"
"""

import telnetlib
from ansible.plugins.connection import ConnectionBase
from ansible.errors import AnsibleError, AnsibleConnectionFailure

import re

terminal_stderr_re = [
    re.compile(r"% ?Error: "),
    re.compile(r"^% \w+", re.M),
    re.compile(r"% ?Bad secret"),
    re.compile(r"invalid input", re.I),
    re.compile(r"(?:incomplete|ambiguous) command", re.I),
    re.compile(r"connection timed out", re.I),
    re.compile(r"[^\r\n]+ not found", re.I),
    re.compile(r"'[^']' +returned error code: ?\d+"),
    re.compile(r"syntax error"),
    re.compile(r"unknown command"),
    re.compile(r"command not found"),
    re.compile(r"Error\[\d+\]: ", re.I),
    re.compile(r"Error:", re.I)
]

login_success_prompts_re = [
    r"[\r\n]*?.+#",
    r"[\r\n]*?<.+>",
    r"[\r\n]*?<.+>(?:\s*)$",
    r"[\r\n]*?<.+>(?:\s*)#",
    r'[\r\n]*?\[.+\](?:\s*)$',
    r'[\r\n]*?\[.+\](?:\s*)$',
]

login_failed_prompts_re = [r"% Login invalid", r"Login incorrect" r"[\r\n]+?login: ", r"[\r\n]+?Username: "]

user_name_prompts_re = [r"login: ", r"Username: "]
password_prompts_re = [r"Password: "]

more_re = [r" --More-- ", r"---- More ----"]


class Connection(ConnectionBase):
    ''' Telnet-based connections '''

    has_pipelining = True
    # while the name of the product is telnet, naming that module telnet cause
    # trouble with module import
    transport = 'telnet'

    def __init__(self, *args, **kwargs):
        super(Connection, self).__init__(*args, **kwargs)

        self.host = self._play_context.remote_addr
        self.port = self._play_context.port or 23
        self.user = self._play_context.remote_user
        self.password = self._play_context.password
        self.timeout = self._play_context.timeout or 10
        self.prompt_words = "$ "

    def _connect(self):
        self._connected = True
        return self

    def _connect_telnet(self):
        try:
            client = telnetlib.Telnet(host=self.host, port=self.port, timeout=self.timeout)
        except Exception, e:
            raise AnsibleConnectionFailure("Failed to connect to the host via telnet: %s" % self.host)
        try:
            if self.user and self.password:
                client.expect(user_name_prompts_re)
                client.write((self.user + "\n").encode("utf8"))
                client.expect(password_prompts_re)
                client.write((self.password + "\n").encode("utf8"))

                index, match, out = client.expect(login_success_prompts_re + login_failed_prompts_re)

                if match and match.re.pattern not in login_failed_prompts_re:
                    prompt_words = match.group()
                    prompt_words = prompt_words.replace("[", "\[")
                    prompt_words = prompt_words.replace("]", "\]")
                    prompt_words = prompt_words.replace("\r\n", "[\r\n]*?")
                    self.prompt_words = prompt_words
                    return client
        except Exception, e:
            pass
        if client:
            client.close()
        raise AnsibleConnectionFailure("Authentication failed.")

    def _get_cmd_result(self, cmd):

        client = self._connect_telnet()

        try:
            out_list = []

            client.write((cmd + "\n").encode("utf8"))

            while True:
                index, match, out = client.expect(more_re + [self.prompt_words])
                backspace_match = re.compile(r"^[\b ]+").match(out)
                if backspace_match:
                    out = out.replace(backspace_match.group(), "")
                if match.re.pattern in more_re:
                    out_list += out.split("\r\n")[0:-1]
                    client.write(" ")
                else:
                    out_list += out.split("\r\n")
                    break

            client.write("exit\n")
            client.close()

            return "\r\n".join(out_list[1:-1])
        except:
            raise AnsibleError("Failed to exec cmd %s on %s" % (cmd, self.host))

    def exec_command(self, cmd, sudoable=True, in_data=None):
        ''' run a command on the remote minion '''
        super(Connection, self).exec_command(cmd, in_data=in_data, sudoable=sudoable)

        self._display.vvv("EXEC %s" % (cmd), host=self.host)

        result = self._get_cmd_result(cmd)

        rc = 1
        stdout = ''
        stderr = ''
        for regex in terminal_stderr_re:
            if regex.findall(result):
                stderr = result
                break
        else:
            rc = 0
            stdout = result

        return (rc, stdout, stderr)

    def put_file(self, in_path, out_path):
        ''' transfer a file from local to remote; nothing to do here '''
        pass

    def fetch_file(self, in_path, out_path):
        ''' fetch a file from remote to local; nothing to do here '''
        pass

    def close(self):
        ''' terminate the connection; nothing to do here '''
        pass


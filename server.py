#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

import os
from SocketServer import TCPServer, BaseRequestHandler
from Crypto.Cipher import AES
from base64 import b64decode, b64encode
import struct
import traceback

__author__ = 'nekocode'


class RequestHandlerr(BaseRequestHandler):
    clients = {}
    ID_LASTEST = 0

    def __init__(self, _request, _client_address, _server):
        BaseRequestHandler.__init__(self, _request, _client_address, _server)

        self.ADDRESS = _client_address
        self.ID = None
        self.IV = '\0' * AES.block_size
        self.SECRET = None

        self.jobs = list()

    def encrypt(self, text):
        encryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        ciphertext = encryptor.encrypt(text)
        return ciphertext

    def decrypt(self, ciphertext):
        decryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        plain = decryptor.decrypt(ciphertext)
        return plain

    def read(self):
        cmd_msg_size = struct.calcsize('!IL')        # 命令标识，消息大小，
        cmd_flag, data_size = struct.unpack('!IL', self.request.recv(cmd_msg_size))

        if cmd_flag == 0:
            # job rlt
            raw = self.request.recv(data_size)      # encrypt
            rlt_info = json.loads(self.decrypt(raw))

        elif cmd_flag == 1:
            # login
            raw = self.request.recv(data_size)
            login_info = json.loads(raw)

            self.SECRET = b64decode(login_info['secret'])

        else:
            print 'unknown command_flag.'
            return

    def handle(self):
        while True:
            self.request.sendall('Hello')

            try:
                data = self.request.recv(1024)

                print "receive from (%r):%r" % (self.client_address, data)
            except:
                traceback.print_exc()


if __name__ == '__main__':
    host = ""       # 主机名
    port = 8080     # 端口
    addr = (host, port)

    server = TCPServer(addr, RequestHandlerr)
    server.serve_forever()


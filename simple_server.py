import tornado.web
import tornado.websocket
import tornado.ioloop
__author__ = 'nekocode'


class BackdoorSocketHandler(tornado.websocket.WebSocketHandler):
    def data_received(self, chunk):
        pass

    def __init__(self, _application, request, **kwargs):
        tornado.websocket.WebSocketHandler.__init__(self, _application, request, **kwargs)

    def on_message(self, message):
        print message


application = tornado.web.Application([
    (r'/', BackdoorSocketHandler)
])


if __name__ == '__main__':
    application.listen(8888, xheaders=True)
    tornado.ioloop.IOLoop.instance().start()


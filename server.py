import tornado.ioloop
import tornado.web
from tornado.httputil import _get_content_range, _parse_request_range
import os
import socket
from config import *

class App:
    def __init__(self):
        self.files = []
        self.max_streams = 4

    def file_response(self):
        pass


class MainHandler(tornado.web.RequestHandler):

    chunk_len = 1024
    content_size = 0

    async def get(self, path, include_body=True):
        # Assume that path is correct, validation will be handeled elsewhere
        absolute_path = os.path.abspath(path)
        print(path)
        path = absolute_path
        if absolute_path is None:
            return

        # self.modified = self.get_modified_time()
        # self.set_headers()
        #
        # if self.should_return_304():
        #     self.set_status(304)
        #     return

        request_range = None
        range_header = self.request.headers.get("Range")
        if range_header:
            # As per RFC 2616 14.16, if an invalid Range header is specified,
            # the request will be treated as if the header didn't exist.
            request_range = _parse_request_range(range_header)
        if request_range:
            start, end = request_range
            await self.set_content_size(absolute_path)
            size = self.content_size
            if (start and (start >= size)) or end == 0:
                # As per RFC 2616 14.35.1, a range is not satisfiable only: if
                # the first requested byte is equal to or greater than the
                # content, or when a suffix with length 0 is specified
                self.set_status(416)  # Range Not Satisfiable
                self.set_header("Content-Type", "text/plain")
                self.set_header("Content-Range", "bytes */%s" % (size,))
                return
            if start and (start < 0):
                start += size
            if end and (end > size):
                # Clients sometimes blindly use a large range to limit their
                # download size; cap the endpoint at the actual file size.
                end = size

            self.set_status(206)  # Partial Content
            self.set_header("Content-Range",
                            _get_content_range(start, end, size))
        else:
            start = end = None

        content = await self.get_content(absolute_path, start, end)
        for chunk in content:
            self.write(chunk)
            tornado.ioloop.IOLoop.current().add_callback(self.flush)
        print('sending success')
        tornado.ioloop.IOLoop.current().add_callback(self.finish)

    async def get_content(self, abspath, start, end):
        with open(abspath, 'rb') as f:
            bts = bytearray(f.read())
        content = []
        point = start
        while point < end:
            point2 = point + self.chunk_len
            point2 = point2 if point2 <= end else end
            content.append(bytes(bts[point: point2]))
            point = point2
        # point = start
        # bts = b'Fuck this Fucking World'
        # while point < end:
        #     point2 = point + self.chunk_len
        #     point2 = point2 if point2 <= end else end
        #     content.append(bts[point: point2])
        # print(content)
        logs.write(str(content))
        return content
    
    async def set_content_size(self, abspath):
        # bts = b'Fuck this Fucking World'
        with open(abspath, 'rb') as f:
            bts = bytearray(f.read())
        self.content_size = len(bts)
        # print(self.content_size)


class Handle(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        return self.render('templates/base.html')

    def get_template_namespace(self):
        namespace = dict(
            handler=self,
            request=self.request,
            current_user=self.current_user,
            locale=self.locale,
            _=self.locale.translate,
            pgettext=self.locale.pgettext,
            static_url=self.static_url,
            xsrf_form_html=self.xsrf_form_html,
            reverse_url=self.reverse_url,
            files=files,
            chunk_num=chunk_num
        )
        namespace.update(self.ui)
        return namespace


if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", Handle),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': "public_root"}),
        (r"/get/(.*)", MainHandler),
    ])
    logs = open('logs', 'w')
    sock = 8888
    application.listen(sock)
    myIP = socket.gethostbyname(socket.gethostname())
    print('*** WebSocket Server Started at %s:%s***' % (myIP, sock))
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print('*** Stopped server ***')
        tornado.ioloop.IOLoop.current().stop()
    logs.close()

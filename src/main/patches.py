# pylint: disable=C0415,W0212
# patch functions import patched modules internally and may access protected members


def patch_gevent(with_check):
    from gevent.monkey import patch_all

    patch_all()

    if with_check:
        import socket

        from gevent import socket as gevent_socket

        if socket.socket is not gevent_socket.socket:
            raise AssertionError

        from requests import utils as requests_utils

        if requests_utils.socket.socket is not gevent_socket.socket:
            raise AssertionError

        from requests.packages.urllib3.util import connection as urllib3_connection  # noqa:E0401

        if urllib3_connection.socket.socket is not gevent_socket.socket:
            raise AssertionError


def patch_gevent_psycopg():
    from psycogreen.gevent import patch_psycopg

    patch_psycopg()


def patch_uwsgi_reason_phrase_logging(application):
    import uwsgi  # noqa:E0401

    def patched_application(environ, start_response):
        response = application(environ, start_response)

        reason_phrase = None
        try:
            reason_phrase = response.reason_phrase
        except AttributeError:
            try:
                reason_phrase = response._response.reason_phrase
            except AttributeError:
                pass

        if reason_phrase:
            uwsgi.set_logvar("reason_phrase", reason_phrase)

        return response

    return patched_application


def patch_runserver_reason_phrase_logging():
    from http import HTTPStatus
    from wsgiref.handlers import SimpleHandler
    from wsgiref.simple_server import ServerHandler

    from django.core.servers.basehttp import WSGIRequestHandler

    # BaseHttp module logs request line with "log_message" method of WSGIRequestHandler.
    # To modify the message, we need to modify "log_request" and "close" methods

    def log_request(self, code="-", size="-", reason_phrase="-"):  # added reason_phrase
        if isinstance(code, HTTPStatus):
            code = code.value
        self.log_message(
            'django %s "%s" %s "%s" render %sb',
            self.address_string(),
            self.requestline,
            str(code),
            str(reason_phrase),
            str(size),
        )

    WSGIRequestHandler.log_request = log_request

    # below is the original ServerHandler.close
    # def log_request(self, code='-', size='-'):
    #     if isinstance(code, HTTPStatus):
    #         code = code.value
    #     self.log_message('"%s" %s %s', self.requestline, str(code), str(size))

    def close(self):
        try:
            code, reason_phrase = self.status.split(" ", 1)
            self.request_handler.log_request(code, self.bytes_sent, reason_phrase)
        finally:
            SimpleHandler.close(self)

    ServerHandler.close = close

    # below is the original ServerHandler.close
    # def close(self):
    #     try:
    #         self.request_handler.log_request(
    #             self.status.split(' ',1)[0], self.bytes_sent
    #         )
    #     finally:
    #         SimpleHandler.close(self)

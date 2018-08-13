from gevent import pywsgi

import falcon
from management_api.config import HOSTNAME, PORT
from management_api.utils.routes import register_routes
from management_api.utils.logger import get_logger

logger = get_logger(__name__)


class AuthMiddleware(object):

    def process_request(self, req, resp):
        token = req.get_header('Authorization')
        if token is None:
            description = ('Please provide an auth token '
                           'as part of the request.')

            raise falcon.HTTPUnauthorized('Auth token required',
                                          description)

        if not self._token_is_valid(token):
            description = ('The provided auth token is not valid. '
                           'Please request a new token and try again.')

            raise falcon.HTTPUnauthorized('Authentication required',
                                          description)

    def _token_is_valid(self, token):
        return True


app = falcon.API(middleware=[AuthMiddleware()])
register_routes(app)


def main():
    pywsgi.WSGIServer((HOSTNAME, PORT),
                      app).serve_forever()


if __name__ == '__main__':
    main()

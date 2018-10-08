from gevent import pywsgi

import falcon


from management_api.config import HOSTNAME, PORT
from management_api.utils.routes import register_routes
from management_api.utils.logger import get_logger
from management_api.utils.errors_handling import add_error_handlers
from management_api.authenticate import AuthMiddleware

logger = get_logger(__name__)


def create_app():
    app = falcon.API(middleware=[AuthMiddleware()])
    add_error_handlers(app)
    register_routes(app)
    return app


def main():
    pywsgi.WSGIServer((HOSTNAME, PORT),
                      create_app()).serve_forever()


if __name__ == '__main__':
    main()

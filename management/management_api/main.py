#
# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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

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

import falcon
import json
import time
import traceback
from urllib.parse import urlparse
from jwt import JWT
from falcon.media.validators import jsonschema

from management_api.config import AuthParameters
from management_api.authenticate.auth_controller import get_auth_controller_url, get_token,\
    get_keys_from_dex
from management_api.utils.logger import get_logger
from management_api.schemas.authenticate import authenticate_token_schema

logger = get_logger(__name__)


class Authenticate():

    def on_get(self, req, resp):
        url = get_auth_controller_url()
        resp.status = falcon.HTTP_308
        resp.set_header('Location', url)


class Token():

    @jsonschema.validate(authenticate_token_schema)
    def on_post(self, req, resp):
        body = req.media
        token = get_token(parameters=body)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'status': 'OK', 'data': {'token': token}})


class TokenDecoder:

    def __init__(self):
        self.key_number = None
        self.keys = None
        self.jwt = JWT()
        self.last_key_fetch = 0
        self.min_key_fetch_time_range = 300.0

    def decode(self, token):
        logger.info("Checking token: {}".format(token))
        if not self.keys:
            self.keys = get_keys_from_dex()
            self.last_key_fetch = time.time()
            logger.info("Fetched keys from dex")
        if self.key_number:
            try:
                logger.debug("Trying to decode key number {}".format(self.key_number))
                return self.jwt.decode(token, self.keys[self.key_number])
            except Exception as e:
                logger.info("Failed to decode token with default key")
                logger.debug(e)
                pass
        for idx, key in enumerate(self.keys):
            try:
                logger.info("Trying key number : {}".format(idx))
                decoded = self.jwt.decode(token, key)
                self.key_number = idx
                logger.info("Decoded")
                return decoded
            except Exception as e:
                logger.info("Failed to decode token, reason: {}".format(str(e)))
                stacktrace = traceback.format_exc()
                logger.debug(stacktrace)
                pass
        logger.info("Failed to verify token with any available key")
        if self.last_key_fetch < time.time() - self.min_key_fetch_time_range:
            logger.info("Fetching new keys from dex and trying again")
            self.keys = None
            return self.decode(token)
        return None


class AuthMiddleware:

    def __init__(self):
        self.admin_endpoints = ['/tenants']
        self.user_endpoints_prefix = '/tenants/'
        self.no_auth_endpoints = ['/authenticate/token', '/authenticate']
        self.admin_user = AuthParameters.ADMIN_SCOPE
        self.system_namespace = AuthParameters.SYSTEM_NAMESPACE
        self.tokenDecoder = TokenDecoder()

    def process_request(self, req, resp):

        path = urlparse(req.url)[2]
        if path in self.no_auth_endpoints:
            return

        token = req.get_header('Authorization')

        if token is None:
            raise falcon.HTTPUnauthorized('Auth token required', 'Missing auth token')

        decoded = self.tokenDecoder.decode(token)
        if not decoded:
            logger.info("Failed to decode token")
            raise falcon.HTTPUnauthorized('Authentication required', "Token not valid.")

        if self._token_expired(decoded):
            raise falcon.HTTPUnauthorized('Authentication required', 'Token expired')

        if path in self.admin_endpoints:
            if not self._token_has_admin_priv(decoded):
                raise falcon.HTTPForbidden('Forbidden', "Insufficient permissions")

        logger.info("Decoded token : {}".format(decoded))
        logger.info("Request : {}".format(req.headers))

    def _token_has_admin_priv(self, decoded):
        if self.admin_user in decoded['groups']:
            return True
        return False

    def _token_expired(self, decoded):
        if decoded['exp'] < time.time():
            return True
        return False

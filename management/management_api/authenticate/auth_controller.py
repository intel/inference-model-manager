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

import requests
import json
from urllib.parse import urlencode, parse_qs, urlparse, urljoin, urlunparse
from requests_oauthlib import OAuth2Session
from jwt import jwk_from_dict
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


from management_api.config import AuthParameters, DEX_URL, PLATFORM_DOMAIN
from management_api.utils.errors_handling import MissingTokenException
from management_api.utils.logger import get_logger

logger = get_logger(__name__)


def get_auth_controller_url():
    auth_controller_url = get_dex_external_url()
    params = {'client_id': AuthParameters.CLIENT_ID, 'redirect_uri': AuthParameters.REDIRECT_URL,
              'response_type': AuthParameters.RESPONSE_TYPE, 'scope': AuthParameters.SCOPE}
    url = urljoin(auth_controller_url, AuthParameters.AUTH_PATH)
    url_parts = list(urlparse(url))
    query = parse_qs(url_parts[4])
    query.update(params)
    url_parts[4] = urlencode(query)
    url = urlunparse(url_parts)
    return url


def get_token(parameters: dict):
    oauth = OAuth2Session(AuthParameters.CLIENT_ID, redirect_uri=AuthParameters.REDIRECT_URL)
    try:
        if 'code' in parameters:
            token = oauth.fetch_token(urljoin(DEX_URL, AuthParameters.TOKEN_PATH),
                                      code=parameters['code'],
                                      client_secret=AuthParameters.CLIENT_SECRET)
        elif 'refresh_token' in parameters:
            extra = {'client_id': AuthParameters.CLIENT_ID,
                     'client_secret': AuthParameters.CLIENT_SECRET}
            token = oauth.refresh_token(urljoin(DEX_URL, AuthParameters.TOKEN_PATH),
                                        refresh_token=parameters['refresh_token'],
                                        **extra)

    except Exception as e:
        raise MissingTokenException(e)

    return token


def _get_keys_from_dex():
    resp = requests.get(urljoin(DEX_URL, "/dex/keys"), params=None)
    data = json.loads(resp.text)
    keys = []
    for k in data['keys']:
        jwk = jwk_from_dict(k)
        keys.append(jwk)
        logger.info("PEM {}".format(jwk.keyobj.
                                    public_bytes(Encoding.PEM,
                                                 PublicFormat.SubjectPublicKeyInfo)
                                    .decode('utf-8')))
    logger.info("Number of imported keys :" + str(len(keys)))
    return keys


def get_dex_external_url():
    host = "dex." + PLATFORM_DOMAIN
    port = 443
    url = f'https://{host}:{port}'
    return url


def get_keys_from_dex():
    return _get_keys_from_dex()

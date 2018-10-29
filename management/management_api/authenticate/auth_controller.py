import requests
import json
from urllib.parse import urlencode, parse_qs, urlparse, urljoin, urlunparse
from requests_oauthlib import OAuth2Session
from jwt import jwk_from_dict
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


from management_api.config import AuthParameters
from management_api.utils.kubernetes_resources import get_dex_external_ip
from management_api.utils.kubernetes_resources import get_k8s_api_client
from management_api.utils.errors_handling import MissingTokenException
from management_api.utils.logger import get_logger

logger = get_logger(__name__)


def get_auth_controller_url():
    api_instance = get_k8s_api_client()
    ip, port = get_dex_external_ip(api_instance)
    auth_controller_url = f'https://{ip}:{port}'
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
    auth_controller_url = get_address_of_dex()
    try:
        if 'code' in parameters:
            token = oauth.fetch_token(urljoin(auth_controller_url, AuthParameters.TOKEN_PATH),
                                      code=parameters['code'], verify=False,
                                      client_secret=AuthParameters.CLIENT_SECRET)
        elif 'refresh_token' in parameters:
            extra = {'client_id': AuthParameters.CLIENT_ID,
                     'client_secret': AuthParameters.CLIENT_SECRET}
            token = oauth.refresh_token(urljoin(auth_controller_url, AuthParameters.TOKEN_PATH),
                                        refresh_token=parameters['refresh_token'], verify=False,
                                        **extra)

    except Exception as e:
        raise MissingTokenException(e)

    return token


def _get_keys_from_dex():
    auth_controller_url = get_address_of_dex()
    resp = requests.get(urljoin(auth_controller_url, "/dex/keys"), params=None, verify=False)
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


def get_keys_from_dex():
    return _get_keys_from_dex()


def get_address_of_dex():
    api_instance = get_k8s_api_client()
    ip, port = get_dex_external_ip(api_instance)
    auth_controller_url = f'https://{ip}:{port}'
    return auth_controller_url
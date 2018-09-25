from management_api.config import AuthParameters
from urllib.parse import urlencode, parse_qs, urlparse, urljoin, urlunparse
from requests_oauthlib import OAuth2Session
from management_api.utils.kubernetes_resources import get_dex_external_ip
from management_api.utils.kubernetes_resources import get_k8s_api_client
from management_api.utils.errors_handling import MissingTokenException


def get_auth_controller_url():
    api_instance = get_k8s_api_client()
    ip, port = get_dex_external_ip(api_instance)
    auth_controller_url = 'https://{ip}:{port}'.format(ip=ip, port=port)
    params = {'client_id': AuthParameters.CLIENT_ID, 'redirect_uri': AuthParameters.REDIRECT_URL,
              'response_type': AuthParameters.RESPONSE_TYPE, 'scope': AuthParameters.SCOPE}
    url = urljoin(auth_controller_url, AuthParameters.AUTH_PATH)
    url_parts = list(urlparse(url))
    query = parse_qs(url_parts[4])
    query.update(params)
    url_parts[4] = urlencode(query)
    url = urlunparse(url_parts)
    return url


def get_token(auth_code: str):
    oauth = OAuth2Session(AuthParameters.CLIENT_ID, redirect_uri=AuthParameters.REDIRECT_URL)
    api_instance = get_k8s_api_client()
    ip, port = get_dex_external_ip(api_instance)
    auth_controller_url = 'https://{ip}:{port}'.format(ip=ip, port=port)
    try:
        token = oauth.fetch_token(urljoin(auth_controller_url, AuthParameters.TOKEN_PATH),
                                  code=auth_code, verify=False,
                                  client_secret=AuthParameters.CLIENT_SECRET)
    except Exception as e:
        raise MissingTokenException(e)

    return token

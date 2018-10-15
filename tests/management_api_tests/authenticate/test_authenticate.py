import requests
import pytest
import json

from management_api_tests.config import AUTH_MANAGEMENT_API_URL, TOKEN_MANAGEMENT_API_URL, JOE
from management_api_tests.authenticate import authenticate


def test_get_auth_redirection():
    url = AUTH_MANAGEMENT_API_URL
    response = requests.get(url, allow_redirects=False)
    assert response.status_code == 308


@pytest.mark.parametrize("body_key, refresh_token", [('code', False), ('refresh_token', True)])
def test_get_token(body_key, refresh_token):
    if 'code' in body_key:
        code = authenticate(username=JOE['login'], password=JOE['password'],
                            token=refresh_token)
    else:
        code = authenticate(username=JOE['login'], password=JOE['password'],
                            token=refresh_token)['refresh_token']
    url = TOKEN_MANAGEMENT_API_URL
    data = json.dumps({
        body_key: code
    })
    response = requests.post(url, data=data)

    assert response.status_code == 200
    assert 'token' in response.text

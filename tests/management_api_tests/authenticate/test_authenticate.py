import requests
import pytest
import json

from management_api_tests.config import AUTH_MANAGEMENT_API_URL, TOKEN_MANAGEMENT_API_URL


def test_get_auth_redirection():
    url = AUTH_MANAGEMENT_API_URL
    response = requests.get(url, allow_redirects=False)
    assert response.status_code == 308


@pytest.mark.xfail(run=False)
def test_get_token():
    auth_code = 'test'
    url = TOKEN_MANAGEMENT_API_URL
    data = json.dumps({
        'code': auth_code
    })
    response = requests.post(url, data=data)

    assert response.status_code == 200

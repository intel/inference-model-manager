from management_api.authenticate.auth_controller import get_auth_controller_url, get_token
from unittest.mock import Mock
import pytest


def test_get_auth_controller_url(external_svc_auth_controller):
    create_custom_client_mock, external_ip_port_mock = external_svc_auth_controller

    external_ip_port_mock.return_value = ['127.0.0.1', 1234]
    url = get_auth_controller_url()
    assert 'redirect_uri' in url and 'response_type' in url and 'client_id' in url
    create_custom_client_mock.assert_called_once()
    external_ip_port_mock.assert_called_once()


@pytest.mark.parametrize("raise_error", [(False), (True)])
def test_get_token(mocker, external_svc_auth_controller, raise_error):
    oauth_session = Mock()
    create_custom_client_mock = mocker.patch('management_api.authenticate.auth_controller.'
                                             'OAuth2Session')
    create_custom_client_mock.return_value = oauth_session

    create_custom_client_mock, external_ip_port_mock = external_svc_auth_controller
    external_ip_port_mock.return_value = ['127.0.0.1', 1234]
    if raise_error:
        oauth_session.fetch_token.side_effect = Exception()
        with pytest.raises(Exception):
            get_token(auth_code='test')
    else:
        returned_message = {'token': 'test'}
        oauth_session.fetch_token.return_value = returned_message
        output = get_token(auth_code='test')
        assert returned_message == output
    oauth_session.fetch_token.assert_called_once()
    create_custom_client_mock.assert_called_once()
    external_ip_port_mock.assert_called_once()
    create_custom_client_mock.assert_called_once()

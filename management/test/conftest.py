from falcon import testing
import pytest
from management_api.main import app
from unittest.mock import Mock


@pytest.fixture(scope='session')
def client():
    return testing.TestClient(app)


@pytest.fixture(scope='function')
def url_to_service_endpoint_utils(mocker):
    mock_return_value = {"test": "test"}
    external_address_mock = mocker.patch('management_api.endpoints.endpoint_utils.'
                                         'create_url_to_service')
    external_address_mock.return_value = mock_return_value
    return external_address_mock, mock_return_value


@pytest.fixture(scope='function')
def custom_client_mock_endpoint_utils(mocker):
    custom_client = Mock()
    create_custom_client_mock = mocker.patch('management_api.endpoints.endpoint_utils.'
                                             'get_k8s_api_custom_client')
    create_custom_client_mock.return_value = custom_client
    return create_custom_client_mock, custom_client


@pytest.fixture(scope='function')
def api_client_mock_endpoint_utils(mocker):
    api_client = Mock()
    create_api_client_mock = mocker.patch('management_api.endpoints.endpoint_utils.'
                                          'get_k8s_api_client')
    create_api_client_mock.return_value = api_client
    return create_api_client_mock, api_client


@pytest.fixture(scope='function')
def external_svc_auth_controller(mocker):
    create_custom_client_mock = mocker.patch('management_api.authenticate.auth_controller.'
                                             'get_k8s_api_client')
    external_ip_port_mock = mocker.patch('management_api.authenticate.auth_controller.'
                                         'get_dex_external_ip')

    return create_custom_client_mock, external_ip_port_mock

from falcon import testing
import pytest
from management_api.main import create_app
from unittest.mock import Mock
from test_utils.auth_middleware_mock import AuthMiddlewareMock
from unittest import mock


@pytest.fixture(scope='session')
def client():
    with mock.patch('management_api.main.AuthMiddleware') as middleware:
        middleware.return_value = AuthMiddlewareMock()
        return testing.TestClient(create_app())


@pytest.fixture(scope='session')
def client_with_auth():
    return testing.TestClient(create_app())


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
def apps_client_mock_endpoint_utils(mocker):
    apps_client = Mock()
    create_apps_client_mock = mocker.patch('management_api.endpoints.endpoint_utils.'
                                           'get_k8s_apps_api_client')
    create_apps_client_mock.return_value = apps_client
    return create_apps_client_mock, apps_client


@pytest.fixture(scope='function')
def external_svc_auth_controller(mocker):
    create_custom_client_mock = mocker.patch('management_api.authenticate.auth_controller.'
                                             'get_k8s_extensions_api_client')
    external_ip_port_mock = mocker.patch('management_api.authenticate.auth_controller.'
                                         'get_dex_external_host')

    return create_custom_client_mock, external_ip_port_mock

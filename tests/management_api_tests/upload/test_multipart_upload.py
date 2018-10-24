import json
import requests
import pytest
from management_api_tests.config import DEFAULT_HEADERS, USER1_HEADERS, \
    START_MULTIPART_UPLOAD_API_URL


@pytest.mark.parametrize("tenant_fix, auth, body, expected_status",
                         [('tenant', DEFAULT_HEADERS, {'modelName': 'resnet2',
                                                       'modelVersion': 1,
                                                       'fileName': 'saved_model.pb'},
                           200),
                          ('tenant', DEFAULT_HEADERS, {'modelName': 'resnet2'},
                           400),
                          ('fake_tenant', USER1_HEADERS, {'modelName': 'resnet2',
                                                          'modelVersion': 1,
                                                          'fileName': 'saved_model.pb'},
                           404),
                          ])
def test_multipart_upload(request, tenant_fix, auth, body, expected_status):
    namespace, _ = request.getfixturevalue(tenant_fix)
    data = json.dumps(body)
    url = START_MULTIPART_UPLOAD_API_URL.format(tenant_name=namespace)
    response = requests.post(url, data=data, headers=auth)
    assert expected_status == response.status_code

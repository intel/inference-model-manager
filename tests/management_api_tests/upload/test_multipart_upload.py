import json
import requests
import pytest
from management_api_tests.config import DEFAULT_HEADERS, START_MULTIPART_UPLOAD_API_URL


@pytest.mark.parametrize("tenant_fix, body, expected_status",
                         [('tenant', {'modelName': 'resnet2', 'modelVersion': 1}, 200),
                          ('tenant', {'modelName': 'resnet2'}, 400),
                          ('fake_tenant', {'modelName': 'resnet2', 'modelVersion': 1}, 404),
                          ])
def test_multipart_upload(request, tenant_fix, body, expected_status):
    headers = DEFAULT_HEADERS
    namespace, _ = request.getfuncargvalue(tenant_fix)
    headers['Authorization'] = namespace
    data = json.dumps(body)
    url = START_MULTIPART_UPLOAD_API_URL

    response = requests.post(url, data=data, headers=headers)
    assert expected_status == response.status_code

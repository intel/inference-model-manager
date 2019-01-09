#
# Copyright (c) 2019 Intel Corporation
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

import json
import requests
import pytest
from config import DEFAULT_HEADERS, USER1_HEADERS, START_MULTIPART_UPLOAD_API_URL, USER2_HEADERS


@pytest.mark.parametrize("tenant_fix, auth, body, expected_status",
                         [('session_tenant', DEFAULT_HEADERS, {'modelName': 'resnet2',
                                                               'modelVersion': 1,
                                                               'fileName': 'saved_model.pb'},
                           200),
                          ('session_tenant', DEFAULT_HEADERS, {'modelName': 'resnet2'}, 400),
                          ('fake_saturn_tenant', USER2_HEADERS, {'modelName': 'resnet2',
                                                                 'modelVersion': 1,
                                                                 'fileName': 'saved_model.pb'},
                           404),
                          ('session_tenant', USER1_HEADERS, {'modelName': 'resnet2',
                                                             'modelVersion': 1,
                                                             'fileName': 'saved_model.pb'}, 403),
                          ])
def test_multipart_upload(request, tenant_fix, auth, body, expected_status):
    namespace, _ = request.getfixturevalue(tenant_fix)
    data = json.dumps(body)
    url = START_MULTIPART_UPLOAD_API_URL.format(tenant_name=namespace)
    response = requests.post(url, data=data, headers=auth)
    assert expected_status == response.status_code

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

import os
from enum import Enum
from config import TENANT_NAME, SCOPE_NAME, CERT


PORTABLE_SECRETS_PATHS = ['mgt-api/minio-access-info', 'mgt-api/tls-secret']

PLATFORM_ADMIN = os.environ.get('PLATFORM_ADMIN', 'platform_admin')


BASE64_DECODING_ERROR_MESSAGE = "Base64 decoding"
INCORRECT_FORMAT_ERROR_MESSAGE = "certificate format"

WRONG_CERTS = [
    ('1goodalphabetwrongpadding==',
     BASE64_DECODING_ERROR_MESSAGE),
    ('G00odAlPhAbEtwr0NgpADD1nG',
     BASE64_DECODING_ERROR_MESSAGE),
    ('49023329489320432843249049032483204932043284903248322390432840832429089034803284324',
     BASE64_DECODING_ERROR_MESSAGE),
    ('!@#$%^&*()_-.:}',
     BASE64_DECODING_ERROR_MESSAGE),
    ('GutPaddingWrongAlphabet.',
     BASE64_DECODING_ERROR_MESSAGE),
    ('ad:98:bc_xd!wtf?lol.',
     BASE64_DECODING_ERROR_MESSAGE),
    ('abcdef123456QWERTY==',
     INCORRECT_FORMAT_ERROR_MESSAGE),
    ('GutPaddingAndGutAlphabet',
     INCORRECT_FORMAT_ERROR_MESSAGE),
    (
    'DRVJUSUZJQ0FURS0tLS0tCk1JSURJVENDQWdtZ0F3SUJBZ0lKQUw1ZGxQc3pYTFlMTUEwR0NTcUdTSWIzRFFFQkN3VUFNQ2N4SlRBakJnTlYKQkFNTUhITmxjblpwYm1jdGMyVnlkbWxqWlM1cmRXSmxMbU5zZFhOMFpYSXdIaGNOTVRnd05qSTJNRGN5TmpJNQpXaGNOTVRrd05qSTJNRGN5TmpJNVdqQW5NU1V3SXdZRFZRUUREQnh6WlhKMmFXNW5MWE5sY25acFkyVXVhM1ZpClpTNWpiSFZ6ZEdWeU1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBNzl0ZE1QS3kKZmpDVkdFbHNMNXRMcDVUeUR0aDhrSFczcUlTU3ZHRVAvVHVzSk9tM1hxbkhoQ1c2aFpSN2tNcWRyd1ZSZUNzVQp6OTVDSnVod0p0TFpSMGVxTVBKbW5EbnhEVmMxb0VVUzE2UTNhOWpqOTBIWTIzZ2h2cXFrcXlYN3cvZzliZnF5CmxuaE16OElYT1JiM0hKVTVWR3V2Q2xMR3ZxNjBOTUxBT3NRZUg3YS9lOU5qdVVWSXdJQTcyenZrQnI0OHcrUWYKMHVGMGVCYUNtOUpobEZLb3d5b3hsN2lWN0FKeHBuS0EyL3M4aHlrMEVoYVhJVE1sUjFmblpnTWF6UEIrV1AvTwpZamJzdmdMNmpNUzR2eTVBbXFXSXJyNkdna2tRdzhOektiRDRSV1U3MWFzenBPQlFVTjlDaE5aVTlzdDkzVjhTCnc4VkFkYWN5WDZXQ2J3SURBUUFCbzFBd1RqQWRCZ05WSFE0RUZnUVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1YKRnlzd0h3WURWUjBqQkJnd0ZvQVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1ZGeXN3REFZRFZSMFRCQVV3QXdFQgovekFOQmdrcWhraUc5dzBCQVFzRkFBT0NBUUVBRjNLSWVrZzl3bndibzhNalhab3Z5ZnIzTXZGT0NiSnIrWkRiCldyajVMSVlSemJkN05BNHZRQkxXeXN1SFVzTVF6UGZUVWJzU3JSTFNEQzdKMGE4c0FaUHYwU1RCL2hpQzRuRDYKVVloWU9uVE95eDFNeUVzQUNUWDJGbWNyQk9wdXliVFlhekdoRXh3QXlEVjFqSmZnanZlMjh0L1RNbVhOeFdJbgpLc0g4S09icTVoTit2bXdnajljakdWbGxSdUdaZFIrZVdoK0ppbEh3dGxaME1URG1jcUd6WDZPclhQZmZnNHJjCkFXN0FtVlpBVnQzSEF4N1FkZ2xxMkZJMGVCa0FFSEVHb0hvM0xsOGU0Z01rUUIyMDhaZmFvdFFSb2xHYkRLb3EKeENMd3NBd3hXVnlhMHl0MUhhRFJmOWRDSUxOcVZCM29TNThiSEFWMEZGV2o5aVE9PQotLS0tLUVORCBDRVJUSUZJQ01FURS0tLS0h3dwe12d3AQ',  # noqa
    INCORRECT_FORMAT_ERROR_MESSAGE),
    (
    'LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURJVENDQWdtZ0F3SUJBZ0lKQUw1ZGxQc3pYTFlMTUEwR0NTcUdTSWIzRFFFQkN3VUFNQ2N4SlRBakJnTlYKQkFNTUhITmxjblpwYm1jdGMyVnlkbWxqWlM1cmRXSmxMbU5zZFhOMFpYSXdIaGNOTVRnd05qSTJNRGN5TmpJNQpXaGNOTVRrd05qSTJNRGN5TmpJNVdqQW5NU1V3SXdZRFZRUUREQnh6WlhKMmFXNW5MWE5sY25acFkyVXVhM1ZpClpTNWpiSFZ6ZEdWeU1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBNzl0ZE1QS3kKZmpDVkdFbHNMNXRMcDVUeUR0aDhrSFczcUlTU3ZHRVAvVHVzSk9tM1hxbkhoQ1c2aFpSN2tNcWRyd1ZSZUNzVQp6OTVDSnVod0p0TFpSMGVxTVBKbW5EbnhEVmMxb0VVUzE2UTNhOWpqOTBIWTIzZ2h2cXFrcXlYN3cvZzliZnF5CmxuaE16OElYT1JiM0hKVTVWR3V2Q2xMR3ZxNjBOTUxBT3NRZUg3YS9lOU5qdVVWSXdJQTcyenZrQnI0OHcrUWYKMHVGMGVCYUNtOUpobEZLb3d5b3hsN2lWN0FKeHBuS0EyL3M4aHlrMEVoYVhJVE1sUjFmblpnTWF6UEIrV1AvTwpZamJzdmdMNmpNUzR2eTVBbXFXSXJyNkdna2tRdzhOektiRDRSV1U3MWFzenBPQlFVTjlDaE5aVTlzdDkzVjhTCnc4VkFkYWN5WDZXQ2J3SURBUUFCbzFBd1RqQWRCZ05WSFE0RUZnUVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1YKRnlzd0h3WURWUjBqQkJnd0ZvQVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1ZGeXN3REFZRFZSMFRCQVV3QXdFQgovekFOQmdrcWhraUc5dzBCQVFzRkFBT0NBUUVBRjNLSWVrZzl3bndibzhNalhab3Z5ZnIzTXZGT0NiSnIrWkRiCldyajVMSVlSemJkN05BNHZRQkxXeXN1SFVzTVF6UGZUVWJzU3JSTFNEQzdKMGE4c0FaUHYwU1RCL2hpQzRuRDYKVVloWU9uVE95eDFNeUVzQUNUWDJGbWNyQk9wdXliVFlhekdoRXh3QXlEVjFqSmZnanZlMjh0L1RNbVhOeFdJbgpLc0g4S09icTVoTit2bXdnajljakdWbGxSdUdaZFIrZVdoK0ppbEh3dGxaME1URG1jcUd6WDZPclhQZmZnNHJjCkFXN0FtVlpBVnQzSEF4N1FkZ2xxMkZJMGVCa0FFSEVHb0hvM0xsOGU0Z01rUUIyMDhaZmFvdFFSb2xHYkRLb3EKeENMd3NBd3hXVnlhMHl0aElKMUhhRFJmOWRDSUxOcVZCM29TNThiSEFWMEZGV2o5aVE9PQotLS0tLUVORCBDRVJU',  # noqa
    INCORRECT_FORMAT_ERROR_MESSAGE),
    (
    'LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURJVENDQWdtZ0F3SUJBZ0lKQUw1ZGxQc3pYTFlMTUEwR0NTcUdTSWIzRFFFQkN3VUFNQ2N4SlRBakJnTlYKQkFNTUhITmxjblpwYm1jdGMyVnlkbWxqWlM1cmRXSmxMbU5zZFhOMFpYSXdIaGNOTVRnd05qSTJNRGN5TmpJNQpXaGNOTVRrd05qSTJNRGN5TmpJNVdqQW5NU1V3SXdZRFZRUUREQnh6WlhKMmFXNW5MWE5sY25acFkyVXVhM1ZpClpTNWpiSFZ6ZEdWeU1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBNzl0ZE1QS3kKZmpDVkdFbHNMNXRMcDVUeUR0aDhrSFczcUlTU3ZHRVAvVHVzSk9tM1hxbkhoQ1c2aFpSN2tNcWRyd1ZSZUNzVQp6OTVDSnVod0p0TFpSMGVxTVBKbW5EbnhEVmMxb0VVUzE2UTNhOWpqOTBIWTIzZ2h2cXFrcXlYN3cvZzliZnF5CmxuaE16OElYT1JiM0hKVTVWR3V2Q2xMR3ZxNjBOTUxBT3NRZUg3YS9lOU5qdVVWSXdJQTcyenZrQnI0OHcrUWYKMHVGMGVCYUNtOUpobEZLb3d5b3hsN2lWN0FKeHBuS0EyL3M4aHlrMEVoYVhJVE1sUjFmblpnTWF6UEIrV1AvTwpZamJzdmdMNmpNUzR2eTVBbXFXSXJyNkdna2tRdzhOektiRDRSV1U3MWFzenBPQlFVTjlDaE5aVTlzdDkzVjhTCnc4VkFkYWN5WDZXQ2J3SURBUUFCbzFBd1RqQWRCZ05WSFE0RUZnUVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1YKRnlzd0h3WURWUjBqQkJnd0ZvQVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1ZGeXN3REFZRFZSMFRCQVV3QXdFQgovekFOQmdrcWhraUc5dzBCQVFzRkFBT0NBUUVBRjNLSWVrZzl3bndibzhNalhab3Z5ZnIzTXZGT0NiSnIrWkRiCldyajVMSVlSemJkN05BNHZRQkxXeXN1SFVzTVF6UGZUVWJzU3JSTFNEQzdKMGE4c0FaUHYwU1RCL2hpQzRuRDYKVVloWU9uVE95eDFNeUVzQUNUWDJGbWNyQk9wdXliVFlhekdoRXh3QXlEVjFqSmZnanZlMjh0L1RNbVhOeFdJbgpLc0g4S09icTVoTit2bXdnajljakdWbGxSdUdaZFIrZVdoK0ppbEh3dGxaME1URG1jcUd6WDZPclhQZmZnNHJjCkFXN0FtVlpBVnQzSEF4N1FkZ2xxMkZJMGVCa0FFSEVHb0hvM0xsOGU0Z01rUUIyMDhaZmFvdFFSb2xHYkRLb3EKeENMd4rBd3hXVnlhMHl0aElKMUhhRFJmOWRDSUxOcVZCM29TNThiSEFWMEZGV2o5aVE9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==',  # noqa
    INCORRECT_FORMAT_ERROR_MESSAGE),
    (
    '1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURJVENDQWdtZ0F3SUJBZ0lKQUw1ZGxQc3pYTFlMTUEwR0NTcUdTSWIzRFFFQkN3VUFNQ2N4SlRBakJnTlYKQkFNTUhITmxjblpwYm1jdGMyVnlkbWxqWlM1cmRXSmxMbU5zZFhOMFpYSXdIaGNOTVRnd05qSTJNRGN5TmpJNQpXaGNOTVRrd05qSTJNRGN5TmpJNVdqQW5NU1V3SXdZRFZRUUREQnh6WlhKMmFXNW5MWE5sY25acFkyVXVhM1ZpClpTNWpiSFZ6ZEdWeU1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBNzl0ZE1QS3kKZmpDVkdFbHNMNXRMcDVUeUR0aDhrSFczcUlTU3ZHRVAvVHVzSk9tM1hxbkhoQ1c2aFpSN2tNcWRyd1ZSZUNzVQp6OTVDSnVod0p0TFpSMGVxTVBKbW5EbnhEVmMxb0VVUzE2UTNhOWpqOTBIWTIzZ2h2cXFrcXlYN3cvZzliZnF5CmxuaE16OElYT1JiM0hKVTVWR3V2Q2xMR3ZxNjBOTUxBT3NRZUg3YS9lOU5qdVVWSXdJQTcyenZrQnI0OHcrUWYKMHVGMGVCYUNtOUpobEZLb3d5b3hsN2lWN0FKeHBuS0EyL3M4aHlrMEVoYVhJVE1sUjFmblpnTWF6UEIrV1AvTwpZamJzdmdMNmpNUzR2eTVBbXFXSXJyNkdna2tRdzhOektiRDRSV1U3MWFzenBPQlFVTjlDaE5aVTlzdDkzVjhTCnc4VkFkYWN5WDZXQ2J3SURBUUFCbzFBd1RqQWRCZ05WSFE0RUZnUVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1YKRnlzd0h3WURWUjBqQkJnd0ZvQVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1ZGeXN3REFZRFZSMFRCQVV3QXdFQgovekFOQmdrcWhraUc5dzBCQVFzRkFBT0NBUUVBRjNLSWVrZzl3bndibzhNalhab3Z5ZnIzTXZGT0NiSnIrWkRiCldyajVMSVlSemJkN05BNHZRQkxXeXN1SFVzTVF6UGZUVWJzU3JSTFNEQzdKMGE4c0FaUHYwU1RCL2hpQzRuRDYKVVloWU9uVE95eDFNeUVzQUNUWDJGbWNyQk9wdXliVFlhekdoRXh3QXlEVjFqSmZnanZlMjh0L1RNbVhOeFdJbgpLc0g4S09icTVoTit2bXdnajljakdWbGxSdUdaZFIrZVdoK0ppbEh3dGxaME1URG1jcUd6WDZPclhQZmZnNHJjCkFXN0FtVlpBVnQzSEF4N1FkZ2xxMkZJMGVCa0FFSEVHb0hvM0xsOGU0Z01rUUIyMDhaZmFvdFFSb2xHYkRLb3EKeENMd3NBd3hXVnlhMHl0aElKMUhhRFJmOWRDSUxOcVZCM29TNThiSEFWMEZGV2o5aVE9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg',  # noqa
    INCORRECT_FORMAT_ERROR_MESSAGE)
]


QUOTA_REGEX = "^([+]?[0-9.]+)([eEinumkKMGTP]*[+]?[0-9]*)$"

QUOTA = {
    'requests.cpu': '1',
    'requests.memory': '1Gi',
    'limits.cpu': '1',
    'limits.memory': '1Gi',
    'maxEndpoints': 1,
}

QUOTA_WRONG_VALUES = [
    ({'requests.cpu': '-1',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': 1},
     "'-1' does not match '{}'"),
    ({'requests.cpu': '1-',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': 1},
     "'1-' does not match '{}'"),
    ({'requests.cpu': 'a',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': 1},
     "'a' does not match '{}'"),
    ({'requests.cpu': '1a',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': 1},
     "'1a' does not match '{}'"),
    ({'requests.cpu': '1',
      'requests.memory': '1Gi',
      'limits.cpu': '-1',
      'limits.memory': '1Gi',
      'maxEndpoints': 1},
     "'-1' does not match '{}'"),
    ({'requests.cpu': '1',
      'requests.memory': '1Gi',
      'limits.cpu': '1a',
      'limits.memory': '1Gi',
      'maxEndpoints': 1},
     "'1a' does not match '{}'"),
    ({'requests.cpu': '1',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': -1},
     "-1 is less than the minimum of 1"),
    ({'requests.cpu': '1',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': 'a'},
     "'a' is not of type 'integer'"),
    ({'requests.cpu': '1',
      'requests.memory': '-1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': 1},
     "'-1Gi' does not match '{}'"),
    ({'requests.cpu': '1',
      'requests.memory': '1Gi-',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': 1},
     "'1Gi-' does not match '{}'"),
    ({'requests.cpu': '1',
      'requests.memory': '1Ga',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': 1},
     "'1Ga' does not match '{}'"),
    ({'requests.cpu': '1',
      'requests.memory': 'a1',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': 1},
     "'a1' does not match '{}'"),
    ({'requests.cpu': '1',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1-Gi',
      'maxEndpoints': 1},
     "'1-Gi' does not match '{}'"),
]

TENANT_NAME_REGEX = "^[a-z0-9]([-a-z0-9]*[a-z0-9])?$"


def wrong_name(name, message):
    return ({'name': name, 'cert': CERT, 'scope': SCOPE_NAME, 'quota': QUOTA},
            400, "'{}' {}".format(name, message.format(TENANT_NAME_REGEX)))


WRONG_BODIES = [
    ({'cert': CERT, 'scope': SCOPE_NAME, 'quota': QUOTA}, 400,
     "'name' is a required property"),
    ({'name': TENANT_NAME, 'cert': CERT, 'quota': QUOTA}, 400,
     "'scope' is a required property"),
    ({'name': TENANT_NAME, 'scope': SCOPE_NAME, 'quota': QUOTA}, 400,
     "'cert' is a required property"),
    ({'name': TENANT_NAME, 'cert': CERT, 'scope': SCOPE_NAME}, 400,
     "'quota' is a required property"),
    wrong_name("_", "does not match '{}'"),
    wrong_name("ten_name", "does not match '{}'"),
    wrong_name('a', 'is too short'),
    wrong_name('veryveryveryveryveryveryveryveryveryveryveryveryverylongtenantname', 'is too long')
]


RESOURCE_NOT_FOUND = 404
NAMESPACE_BEING_DELETED = 409
TERMINATION_IN_PROGRESS = 'Terminating'
NO_SUCH_BUCKET_EXCEPTION = 'NoSuchBucket'


class CheckResult(Enum):
    ERROR = 0
    RESOURCE_AVAILABLE = 100
    RESOURCE_UNAVAILABLE = 101
    RESOURCE_DOES_NOT_EXIST = 102
    RESOURCE_BEING_DELETED = 103
    CONTENTS_MATCHING = 200
    CONTENTS_MISMATCHING = 201


class OperationStatus(Enum):
    FAILURE = 0
    SUCCESS = 1
    TERMINATED = 2
    ONGOING = 3

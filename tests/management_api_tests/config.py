import os
import urllib.parse
from enum import Enum

MINIO_ACCESS_KEY_ID = os.environ.get('MINIO_ACCESS_KEY',
                                     'AKIAIOSFODNN7EXAMPLE')
MINIO_SECRET_ACCESS_KEY = os.environ.get('MINIO_SECRET_KEY',
                                         'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY')
MINIO_ENDPOINT_ADDR = os.environ.get('MINIO_ENDPOINT_ADDR', 'http://127.0.0.1:9000')
MINIO_REGION = os.environ.get('MINIO_REGION', 'us-east-1')
SIGNATURE_VERSION = 's3v4'
PORTABLE_SECRETS_PATHS = ['default/minio-access-info', 'default/tls-secret']

DEFAULT_HEADERS = {
    'accept': 'application/json',
    'Authorization': 'default',
    'Content-Type': 'application/json',
}

CRD_GROUP = 'intel.com'
CRD_VERSION = 'v1'
CRD_PLURAL = 'servers'
CRD_API_VERSION = 'intel.com/v1'
CRD_KIND = 'Server'


# Credentials for Jane which belongs to default and test group
JANE = {'login': "janedoe@example.com", 'password': "foo"}

# Credentials for Joe which belongs in default group
JOE = {'login': "johndoe@example.com", 'password': "bar"}

MANAGEMENT_API_URL = os.environ.get('MANAGEMENT_API_URL', 'http://127.0.0.1:5000')
TENANTS_MANAGEMENT_API_URL = urllib.parse.urljoin(MANAGEMENT_API_URL, 'tenants')
ENDPOINT_MANAGEMENT_API_URL = urllib.parse.urljoin(MANAGEMENT_API_URL, 'endpoints')
ENDPOINT_MANAGEMENT_API_URL_SCALE = ENDPOINT_MANAGEMENT_API_URL + "/{endpoint_name}/scaling"
ENDPOINT_MANAGEMENT_API_URL_UPDATE = ENDPOINT_MANAGEMENT_API_URL + "/{endpoint_name}/updating"
START_MULTIPART_UPLOAD_API_URL = urllib.parse.urljoin(MANAGEMENT_API_URL, 'upload/start')
AUTH_MANAGEMENT_API_URL = urllib.parse.urljoin(MANAGEMENT_API_URL, 'authenticate')
TOKEN_MANAGEMENT_API_URL = urllib.parse.urljoin(MANAGEMENT_API_URL, 'authenticate/token')

TENANT_NAME = os.environ.get('TENANT_NAME', 'test')

WRONG_TENANT_NAMES = [
    ('_',
     "wrong format"),
    ('ten_name',
     "wrong format"),
    ('a',
     "too short"),
    ('veryveryveryveryveryveryveryveryveryveryveryveryverylongtenantname',
     "too long")
]

CERT = os.environ.get('CERT',
                      'LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURJVENDQWdtZ0F3SUJBZ0lKQUw1ZGxQc3pYTFlMTUEwR0NTcUdTSWIzRFFFQkN3VUFNQ2N4SlRBakJnTlYKQkFNTUhITmxjblpwYm1jdGMyVnlkbWxqWlM1cmRXSmxMbU5zZFhOMFpYSXdIaGNOTVRnd05qSTJNRGN5TmpJNQpXaGNOTVRrd05qSTJNRGN5TmpJNVdqQW5NU1V3SXdZRFZRUUREQnh6WlhKMmFXNW5MWE5sY25acFkyVXVhM1ZpClpTNWpiSFZ6ZEdWeU1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBNzl0ZE1QS3kKZmpDVkdFbHNMNXRMcDVUeUR0aDhrSFczcUlTU3ZHRVAvVHVzSk9tM1hxbkhoQ1c2aFpSN2tNcWRyd1ZSZUNzVQp6OTVDSnVod0p0TFpSMGVxTVBKbW5EbnhEVmMxb0VVUzE2UTNhOWpqOTBIWTIzZ2h2cXFrcXlYN3cvZzliZnF5CmxuaE16OElYT1JiM0hKVTVWR3V2Q2xMR3ZxNjBOTUxBT3NRZUg3YS9lOU5qdVVWSXdJQTcyenZrQnI0OHcrUWYKMHVGMGVCYUNtOUpobEZLb3d5b3hsN2lWN0FKeHBuS0EyL3M4aHlrMEVoYVhJVE1sUjFmblpnTWF6UEIrV1AvTwpZamJzdmdMNmpNUzR2eTVBbXFXSXJyNkdna2tRdzhOektiRDRSV1U3MWFzenBPQlFVTjlDaE5aVTlzdDkzVjhTCnc4VkFkYWN5WDZXQ2J3SURBUUFCbzFBd1RqQWRCZ05WSFE0RUZnUVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1YKRnlzd0h3WURWUjBqQkJnd0ZvQVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1ZGeXN3REFZRFZSMFRCQVV3QXdFQgovekFOQmdrcWhraUc5dzBCQVFzRkFBT0NBUUVBRjNLSWVrZzl3bndibzhNalhab3Z5ZnIzTXZGT0NiSnIrWkRiCldyajVMSVlSemJkN05BNHZRQkxXeXN1SFVzTVF6UGZUVWJzU3JSTFNEQzdKMGE4c0FaUHYwU1RCL2hpQzRuRDYKVVloWU9uVE95eDFNeUVzQUNUWDJGbWNyQk9wdXliVFlhekdoRXh3QXlEVjFqSmZnanZlMjh0L1RNbVhOeFdJbgpLc0g4S09icTVoTit2bXdnajljakdWbGxSdUdaZFIrZVdoK0ppbEh3dGxaME1URG1jcUd6WDZPclhQZmZnNHJjCkFXN0FtVlpBVnQzSEF4N1FkZ2xxMkZJMGVCa0FFSEVHb0hvM0xsOGU0Z01rUUIyMDhaZmFvdFFSb2xHYkRLb3EKeENMd3NBd3hXVnlhMHl0aElKMUhhRFJmOWRDSUxOcVZCM29TNThiSEFWMEZGV2o5aVE9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==')  # noqa

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

SCOPE_NAME = os.environ.get('SCOPE_NAME', 'scope_name')

QUOTA = {
    'requests.cpu': '1',
    'requests.memory': '1Gi',
    'limits.cpu': '1',
    'limits.memory': '1Gi',
    'maxEndpoints': '1',
}

WRONG_BODIES = [
    ({'cert': CERT, 'scope': SCOPE_NAME, 'quota': QUOTA},
     "name"),
    ({'name': TENANT_NAME, 'cert': CERT, 'quota': QUOTA},
     "scope"),
    ({'name': TENANT_NAME, 'scope': SCOPE_NAME, 'quota': QUOTA},
     "cert"),
    ({'name': TENANT_NAME, 'cert': CERT, 'scope': SCOPE_NAME},
     "quota"),
]

QUOTA_WRONG_VALUES = [
    ({'requests.cpu': '-1',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     "requests.cpu field"),

    ({'requests.cpu': '1-',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     "requests.cpu field"),

    ({'requests.cpu': 'a',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     "requests.cpu field"),

    ({'requests.cpu': '1a',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     "requests.cpu field"),

    ({'requests.cpu': '1',
      'requests.memory': '1Gi',
      'limits.cpu': '-1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     "limits.cpu field"),

    ({'requests.cpu': '1',
      'requests.memory': '1Gi',
      'limits.cpu': '1a',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     "limits.cpu field"),

    ({'requests.cpu': '1',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '-1'},
     "maxEndpoints"),

    ({'requests.cpu': '1',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': 'a'},
     "maxEndpoints"),

    ({'requests.cpu': '1',
      'requests.memory': '-1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     "requests.memory field"),

    ({'requests.cpu': '1',
      'requests.memory': '1Gi-',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     "requests.memory field"),

    ({'requests.cpu': '1',
      'requests.memory': '1Ga',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     "requests.memory field"),

    ({'requests.cpu': '1',
      'requests.memory': 'a1',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     "requests.memory field"),

    ({'requests.cpu': '1',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1-Gi',
      'maxEndpoints': '1'},
     "limits.memory field"),
]

TENANT_RESOURCES = {'limits.cpu': '2', 'limits.memory': '2Gi', 'requests.cpu': '1',
                    'requests.memory': '1Gi'}
ENDPOINT_RESOURCES = {'limits.cpu': '200m', 'limits.memory': '200Mi', 'requests.cpu': '100m',
                      'requests.memory': '100Mi'}

QUOTA_INCOMPLIANT_VALUES = [
    ({}, "No resources provided"),
    ({'requests.cpu': '1'}, "Missing resources values"),
]
FAILING_UPDATE_PARAMS = [
    ("wrong_auth", "predict", {'modelName': 'super-model', 'modelVersion': 3}, "Not Found"),
    (TENANT_NAME, "wrong_name", {'modelName': 'super-model', 'modelVersion': 3}, "Not Found"),
    (TENANT_NAME, "predict", {'modelName': 0, 'modelVersion': 3}, "Unprocessable Entity"),
    (TENANT_NAME, "predict", {'modelName': 'super-model', 'modelVersion': "str"},
     "Unprocessable Entity"),
    (TENANT_NAME, "predict", {'modelVersion': 3}, "modelName parameter required"),
    (TENANT_NAME, "predict", {'modelName': 'super-model'}, "modelVersion parameter required"),
]

FAILING_SCALE_PARAMS = [
    ("wrong_auth", "predict", {'replicas': 3}, "Not Found"),
    (TENANT_NAME, "wrong_name", {'replicas': 3}, "Not Found"),
    (TENANT_NAME, "predict", {'replicas': -1}, "Unprocessable Entity"),
    (TENANT_NAME, "predict", {'replicas': "many"}, "Unprocessable Entity"),
    (TENANT_NAME, "predict", {}, "replicas parameter required"),
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

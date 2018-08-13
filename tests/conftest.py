import os
from kubernetes import config, client


# TF serving tests
TFSERVING_HOST_NAME = os.environ.get('HOST_NAME', "resnet.serving-service.com")
TFSERVING_HOST_PORT = os.environ.get('HOST_PORT', 443)

# Management API tests
DEFAULT_HEADERS = {
    'accept': 'application/json',
    'Authorization': 'gg',
    'Content-Type': 'application/json',
}

MANAGEMENT_API_URL = os.environ.get('MANAGEMENT_API_URL', 'http://localhost:5000/tenants')

TENANT_NAME = os.environ.get('TENANT_NAME', 'test')

WRONG_TENANT_NAMES = [
    ('_',
     """{"title": "Tenant name _ is not valid: must consist of lower case alphanumeric characters or '-', and must start and end with an alphanumeric character (e.g. 'my-name', or '123-abc')"}"""),
    ('ten_name',
     """{"title": "Tenant name ten_name is not valid: must consist of lower case alphanumeric characters or '-', and must start and end with an alphanumeric character (e.g. 'my-name', or '123-abc')"}"""),
    ('a',
     """{"title": "Tenant name a is not valid: too short. Provide a tenant name which is at least 3 character long"}"""),
    ('veryveryveryveryveryveryveryveryveryveryveryveryverylongtenantname',
     """{"title": "Tenant name veryveryveryveryveryveryveryveryveryveryveryveryverylongtenantname is not valid: too long. Provide a tenant name which is max 63 character long"}""")
]

CERT = os.environ.get('CERT',
                      'LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURJVENDQWdtZ0F3SUJBZ0lKQUw1ZGxQc3pYTFlMTUEwR0NTcUdTSWIzRFFFQkN3VUFNQ2N4SlRBakJnTlYKQkFNTUhITmxjblpwYm1jdGMyVnlkbWxqWlM1cmRXSmxMbU5zZFhOMFpYSXdIaGNOTVRnd05qSTJNRGN5TmpJNQpXaGNOTVRrd05qSTJNRGN5TmpJNVdqQW5NU1V3SXdZRFZRUUREQnh6WlhKMmFXNW5MWE5sY25acFkyVXVhM1ZpClpTNWpiSFZ6ZEdWeU1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBNzl0ZE1QS3kKZmpDVkdFbHNMNXRMcDVUeUR0aDhrSFczcUlTU3ZHRVAvVHVzSk9tM1hxbkhoQ1c2aFpSN2tNcWRyd1ZSZUNzVQp6OTVDSnVod0p0TFpSMGVxTVBKbW5EbnhEVmMxb0VVUzE2UTNhOWpqOTBIWTIzZ2h2cXFrcXlYN3cvZzliZnF5CmxuaE16OElYT1JiM0hKVTVWR3V2Q2xMR3ZxNjBOTUxBT3NRZUg3YS9lOU5qdVVWSXdJQTcyenZrQnI0OHcrUWYKMHVGMGVCYUNtOUpobEZLb3d5b3hsN2lWN0FKeHBuS0EyL3M4aHlrMEVoYVhJVE1sUjFmblpnTWF6UEIrV1AvTwpZamJzdmdMNmpNUzR2eTVBbXFXSXJyNkdna2tRdzhOektiRDRSV1U3MWFzenBPQlFVTjlDaE5aVTlzdDkzVjhTCnc4VkFkYWN5WDZXQ2J3SURBUUFCbzFBd1RqQWRCZ05WSFE0RUZnUVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1YKRnlzd0h3WURWUjBqQkJnd0ZvQVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1ZGeXN3REFZRFZSMFRCQVV3QXdFQgovekFOQmdrcWhraUc5dzBCQVFzRkFBT0NBUUVBRjNLSWVrZzl3bndibzhNalhab3Z5ZnIzTXZGT0NiSnIrWkRiCldyajVMSVlSemJkN05BNHZRQkxXeXN1SFVzTVF6UGZUVWJzU3JSTFNEQzdKMGE4c0FaUHYwU1RCL2hpQzRuRDYKVVloWU9uVE95eDFNeUVzQUNUWDJGbWNyQk9wdXliVFlhekdoRXh3QXlEVjFqSmZnanZlMjh0L1RNbVhOeFdJbgpLc0g4S09icTVoTit2bXdnajljakdWbGxSdUdaZFIrZVdoK0ppbEh3dGxaME1URG1jcUd6WDZPclhQZmZnNHJjCkFXN0FtVlpBVnQzSEF4N1FkZ2xxMkZJMGVCa0FFSEVHb0hvM0xsOGU0Z01rUUIyMDhaZmFvdFFSb2xHYkRLb3EKeENMd3NBd3hXVnlhMHl0aElKMUhhRFJmOWRDSUxOcVZCM29TNThiSEFWMEZGV2o5aVE9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==')

BASE64_DECODING_ERROR_MESSAGE = """{"title": "Incorrect certificate data in request body. Base64 decoding failure."}"""
INCORRECT_FORMAT_ERROR_MESSAGE = """{"title": "Incorrect certificate format"}"""

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
    ('LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tDQpNSUlGSVRDQ0F3bWdBd0lCQWdJSkFQMUpTL283ZEt3WE1BMEdDU3FHU0liM0RRRUJDd1VBTUNjeEpUQWpCZ05WDQpCQU1NSEhObGNuWnBibWN0YzJWeWRtbGpaUzVyZFdKbExtTnNkWE4wWlhJd0hoY05NVGd3T0RBeE1EZ3dPVE00DQpXaGNOTVRrd09EQXhNRGd3T1RNNFdqQW5NU1V3SXdZRFZRUUREQnh6WlhKMmFXNW5MWE5sY25acFkyVXVhM1ZpDQpaUzVqYkhWemRHVnlNSUlDSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQWc4QU1JSUNDZ0tDQWd.FQXV5R24vSTZ1DQp2dzNQcXdaN0pPVVRNdlNiL3ZiajRaNE5hTFdTb2J5dlFMT2JHNndrVzdkOW11c1M3clRSRGN0QUVqaVBTVktXDQp4eDhrcklXSkZmR05tZlVjQnNjbWwzMVpVeThiVUJCMVdIT2ZoM2dZT1h3SXUvZDFHR0gyaWQ3ZH.hScHJJY1hkDQphSkM3TjRFQjltNEVkaWFSbjNGRGRsNm5FcDlUU1pSVy8xazJyTmpyRlVpUUh4NU5PRk96NEVVRDJ4YWh6cVB5DQpPUnhHV3lHdVRmQmhGb21NWWRGT3pUS09sVXZuVDc3UDh4WEhEbFF.PZWNCN0RvWkdhTjBsUnRSOWpUREJFRmVMDQovYlgrYWI2YW5kTFk3OEx3N1NQYjZsQWF0QmdRWWZBVzV0ZlVVNGVJb:GNGSjE4SFJ5b2I3SiswUFh1YkZlUVFlDQp1enBsMHg4WTVCdndKazVYV1RLakhpNDFMNkJ5amF6K0c2QzB6VzFCM2pOY0tWYXZuYjBsSlhTejkzcUNyeUMrDQpsQVU5WFFiMmhXcTBib3o0ZGhBbm9mWVV2Vi9sNGJnekV1U2tGamp2ZlRIRGpXdUYwWUtwQ0ZWdlBQVUh2UE91DQpSSmtkNWxMNDFObTNMZFVHbUdEcEZhQ29mSWp3NjI4bHFEZ1dJbUJ4UGtLRURLUnRnWmtkcElKRlJSdVNYcll4DQpIWThqNkhvT0ZqR2dSSDZ3TTFHdmJyb3h2bk0vZ01xWHhrOXArMXZZQWVPdmtHVlBFNS9pMWVDbDM5bjdqTExzDQpTcjNFQmhTTFFxb2srMGMvVnE3cVFSck4vZktWd2pEOW5FcGJyQmR5YStWelozTVJ2QkE5WDBHbjVnb3BhdjJxDQpVL0p1ajg1RGNaUG5iVGI4a0ZlVzFWOGNkT1ZwengzV0Ixa0NBd0VBQWFOUU1FNHdIUVlEVlIwT0JCWUVGTkdXDQpjSURBdFhyTFFMSHpRb0hpa2MvVEpBeXpNQjhHQTFVZEl3UVlNQmFBRk5HV2NJREF0WHJMUUxIelFvSGlrYy9UDQpKQXl6TUF3R0ExVWRFd1FGTUFNQkFmOHdEUVlKS29aSWh2Y05BUUVMQlFBRGdnSUJBTEpoYm1hMXNYSFdnaWNmDQpjTmNEZ0Z5OEcyV2N4dk1ja2s2MkE3ZGw1ODhVUW1VYnBHbEpicVJ5Q0Evak1lNERhOEFFSHUrWUxCRkVjRURVDQo5V2liS3AyQ0xkVFlwYnBDbzRxeXhBallRZ2lCdWlJNms3aWJuMG9DSVBhTFZRelcxKzlac21SVEFtSTg1cWpqDQpscTQwS3UvZEgxeXdua2RKemNBNDE1V3h1MFU5a3hyVktZUzRheG1pRENRdlI1bmxJeDdGcHdlNVEybEgrZllMDQpJYVIxMVNPcGVpMFZlcEQvb0tQcHp0Mk05dmZ0OW9ReEVTZ3NLaGd2RmdmTHhJbjlrMXRZRDkwdFBkb2w5dzBEDQoxblFqbkZZc1c1VG9LOGJ3UHc2WnJWY05VY0Q3ZWhGYnJyTDNOMUZ5TWFIWHIwWjd4d2lpbHZSWjdQOEM0ZjE5DQoxZkR5ZDZvS29XcU5teDlBQmlJcEdjeFd1NE9pY2swQnkrcmhVQks3My80ZXFpZS9GeDdFd0ZNbEdtRHFLdlNmDQpIWjJua1YyOFpDWHM4WHNzNVZvRFRkSzR6alRjVXNSdmdNSG5XZUVOT2RTaXNXMm9tcGFYc2xHdjRER3U0SXplDQorYk11cnhQOUIwRXp6T0hpNlVOYmhvUVBGYy9DNkYxQ0hsZ2Qra3BPaHlPdno2dmxNNEtsMmp5YTRDWWVvWWF3DQpmbEZ1UE1CMElKMlZlZ1puWFVyd0VRYXBrM0JFODF1NTRaNzR3Q3greE5LbFdhTWZhN2Vmb1I0K0J2Tkw0VkZ4DQpxTHNMSVJrM202aUpDcmMvR3F4eVJOdTAyZDJyQXBFMEpGNklITmFtY292UWdKUmg3OHVvZ3Fyekc1SXlhR2kwDQpnVHZoT3FpSkthM1pGV2ErNnA0TTRzNE03TndtDQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tDQo=',
     BASE64_DECODING_ERROR_MESSAGE),
    ('abcdef123456QWERTY==',
     INCORRECT_FORMAT_ERROR_MESSAGE),
    ('GutPaddingAndGutAlphabet',
     INCORRECT_FORMAT_ERROR_MESSAGE),
    ('DRVJUSUZJQ0FURS0tLS0tCk1JSURJVENDQWdtZ0F3SUJBZ0lKQUw1ZGxQc3pYTFlMTUEwR0NTcUdTSWIzRFFFQkN3VUFNQ2N4SlRBakJnTlYKQkFNTUhITmxjblpwYm1jdGMyVnlkbWxqWlM1cmRXSmxMbU5zZFhOMFpYSXdIaGNOTVRnd05qSTJNRGN5TmpJNQpXaGNOTVRrd05qSTJNRGN5TmpJNVdqQW5NU1V3SXdZRFZRUUREQnh6WlhKMmFXNW5MWE5sY25acFkyVXVhM1ZpClpTNWpiSFZ6ZEdWeU1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBNzl0ZE1QS3kKZmpDVkdFbHNMNXRMcDVUeUR0aDhrSFczcUlTU3ZHRVAvVHVzSk9tM1hxbkhoQ1c2aFpSN2tNcWRyd1ZSZUNzVQp6OTVDSnVod0p0TFpSMGVxTVBKbW5EbnhEVmMxb0VVUzE2UTNhOWpqOTBIWTIzZ2h2cXFrcXlYN3cvZzliZnF5CmxuaE16OElYT1JiM0hKVTVWR3V2Q2xMR3ZxNjBOTUxBT3NRZUg3YS9lOU5qdVVWSXdJQTcyenZrQnI0OHcrUWYKMHVGMGVCYUNtOUpobEZLb3d5b3hsN2lWN0FKeHBuS0EyL3M4aHlrMEVoYVhJVE1sUjFmblpnTWF6UEIrV1AvTwpZamJzdmdMNmpNUzR2eTVBbXFXSXJyNkdna2tRdzhOektiRDRSV1U3MWFzenBPQlFVTjlDaE5aVTlzdDkzVjhTCnc4VkFkYWN5WDZXQ2J3SURBUUFCbzFBd1RqQWRCZ05WSFE0RUZnUVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1YKRnlzd0h3WURWUjBqQkJnd0ZvQVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1ZGeXN3REFZRFZSMFRCQVV3QXdFQgovekFOQmdrcWhraUc5dzBCQVFzRkFBT0NBUUVBRjNLSWVrZzl3bndibzhNalhab3Z5ZnIzTXZGT0NiSnIrWkRiCldyajVMSVlSemJkN05BNHZRQkxXeXN1SFVzTVF6UGZUVWJzU3JSTFNEQzdKMGE4c0FaUHYwU1RCL2hpQzRuRDYKVVloWU9uVE95eDFNeUVzQUNUWDJGbWNyQk9wdXliVFlhekdoRXh3QXlEVjFqSmZnanZlMjh0L1RNbVhOeFdJbgpLc0g4S09icTVoTit2bXdnajljakdWbGxSdUdaZFIrZVdoK0ppbEh3dGxaME1URG1jcUd6WDZPclhQZmZnNHJjCkFXN0FtVlpBVnQzSEF4N1FkZ2xxMkZJMGVCa0FFSEVHb0hvM0xsOGU0Z01rUUIyMDhaZmFvdFFSb2xHYkRLb3EKeENMd3NBd3hXVnlhMHl0MUhhRFJmOWRDSUxOcVZCM29TNThiSEFWMEZGV2o5aVE9PQotLS0tLUVORCBDRVJUSUZJQ01FURS0tLS0h3dwe12d3AQ',
     INCORRECT_FORMAT_ERROR_MESSAGE),
    ('LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURJVENDQWdtZ0F3SUJBZ0lKQUw1ZGxQc3pYTFlMTUEwR0NTcUdTSWIzRFFFQkN3VUFNQ2N4SlRBakJnTlYKQkFNTUhITmxjblpwYm1jdGMyVnlkbWxqWlM1cmRXSmxMbU5zZFhOMFpYSXdIaGNOTVRnd05qSTJNRGN5TmpJNQpXaGNOTVRrd05qSTJNRGN5TmpJNVdqQW5NU1V3SXdZRFZRUUREQnh6WlhKMmFXNW5MWE5sY25acFkyVXVhM1ZpClpTNWpiSFZ6ZEdWeU1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBNzl0ZE1QS3kKZmpDVkdFbHNMNXRMcDVUeUR0aDhrSFczcUlTU3ZHRVAvVHVzSk9tM1hxbkhoQ1c2aFpSN2tNcWRyd1ZSZUNzVQp6OTVDSnVod0p0TFpSMGVxTVBKbW5EbnhEVmMxb0VVUzE2UTNhOWpqOTBIWTIzZ2h2cXFrcXlYN3cvZzliZnF5CmxuaE16OElYT1JiM0hKVTVWR3V2Q2xMR3ZxNjBOTUxBT3NRZUg3YS9lOU5qdVVWSXdJQTcyenZrQnI0OHcrUWYKMHVGMGVCYUNtOUpobEZLb3d5b3hsN2lWN0FKeHBuS0EyL3M4aHlrMEVoYVhJVE1sUjFmblpnTWF6UEIrV1AvTwpZamJzdmdMNmpNUzR2eTVBbXFXSXJyNkdna2tRdzhOektiRDRSV1U3MWFzenBPQlFVTjlDaE5aVTlzdDkzVjhTCnc4VkFkYWN5WDZXQ2J3SURBUUFCbzFBd1RqQWRCZ05WSFE0RUZnUVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1YKRnlzd0h3WURWUjBqQkJnd0ZvQVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1ZGeXN3REFZRFZSMFRCQVV3QXdFQgovekFOQmdrcWhraUc5dzBCQVFzRkFBT0NBUUVBRjNLSWVrZzl3bndibzhNalhab3Z5ZnIzTXZGT0NiSnIrWkRiCldyajVMSVlSemJkN05BNHZRQkxXeXN1SFVzTVF6UGZUVWJzU3JSTFNEQzdKMGE4c0FaUHYwU1RCL2hpQzRuRDYKVVloWU9uVE95eDFNeUVzQUNUWDJGbWNyQk9wdXliVFlhekdoRXh3QXlEVjFqSmZnanZlMjh0L1RNbVhOeFdJbgpLc0g4S09icTVoTit2bXdnajljakdWbGxSdUdaZFIrZVdoK0ppbEh3dGxaME1URG1jcUd6WDZPclhQZmZnNHJjCkFXN0FtVlpBVnQzSEF4N1FkZ2xxMkZJMGVCa0FFSEVHb0hvM0xsOGU0Z01rUUIyMDhaZmFvdFFSb2xHYkRLb3EKeENMd3NBd3hXVnlhMHl0aElKMUhhRFJmOWRDSUxOcVZCM29TNThiSEFWMEZGV2o5aVE9PQotLS0tLUVORCBDRVJU',
     INCORRECT_FORMAT_ERROR_MESSAGE),
    ('LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURJVENDQWdtZ0F3SUJBZ0lKQUw1ZGxQc3pYTFlMTUEwR0NTcUdTSWIzRFFFQkN3VUFNQ2N4SlRBakJnTlYKQkFNTUhITmxjblpwYm1jdGMyVnlkbWxqWlM1cmRXSmxMbU5zZFhOMFpYSXdIaGNOTVRnd05qSTJNRGN5TmpJNQpXaGNOTVRrd05qSTJNRGN5TmpJNVdqQW5NU1V3SXdZRFZRUUREQnh6WlhKMmFXNW5MWE5sY25acFkyVXVhM1ZpClpTNWpiSFZ6ZEdWeU1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBNzl0ZE1QS3kKZmpDVkdFbHNMNXRMcDVUeUR0aDhrSFczcUlTU3ZHRVAvVHVzSk9tM1hxbkhoQ1c2aFpSN2tNcWRyd1ZSZUNzVQp6OTVDSnVod0p0TFpSMGVxTVBKbW5EbnhEVmMxb0VVUzE2UTNhOWpqOTBIWTIzZ2h2cXFrcXlYN3cvZzliZnF5CmxuaE16OElYT1JiM0hKVTVWR3V2Q2xMR3ZxNjBOTUxBT3NRZUg3YS9lOU5qdVVWSXdJQTcyenZrQnI0OHcrUWYKMHVGMGVCYUNtOUpobEZLb3d5b3hsN2lWN0FKeHBuS0EyL3M4aHlrMEVoYVhJVE1sUjFmblpnTWF6UEIrV1AvTwpZamJzdmdMNmpNUzR2eTVBbXFXSXJyNkdna2tRdzhOektiRDRSV1U3MWFzenBPQlFVTjlDaE5aVTlzdDkzVjhTCnc4VkFkYWN5WDZXQ2J3SURBUUFCbzFBd1RqQWRCZ05WSFE0RUZnUVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1YKRnlzd0h3WURWUjBqQkJnd0ZvQVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1ZGeXN3REFZRFZSMFRCQVV3QXdFQgovekFOQmdrcWhraUc5dzBCQVFzRkFBT0NBUUVBRjNLSWVrZzl3bndibzhNalhab3Z5ZnIzTXZGT0NiSnIrWkRiCldyajVMSVlSemJkN05BNHZRQkxXeXN1SFVzTVF6UGZUVWJzU3JSTFNEQzdKMGE4c0FaUHYwU1RCL2hpQzRuRDYKVVloWU9uVE95eDFNeUVzQUNUWDJGbWNyQk9wdXliVFlhekdoRXh3QXlEVjFqSmZnanZlMjh0L1RNbVhOeFdJbgpLc0g4S09icTVoTit2bXdnajljakdWbGxSdUdaZFIrZVdoK0ppbEh3dGxaME1URG1jcUd6WDZPclhQZmZnNHJjCkFXN0FtVlpBVnQzSEF4N1FkZ2xxMkZJMGVCa0FFSEVHb0hvM0xsOGU0Z01rUUIyMDhaZmFvdFFSb2xHYkRLb3EKeENMd4rBd3hXVnlhMHl0aElKMUhhRFJmOWRDSUxOcVZCM29TNThiSEFWMEZGV2o5aVE9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==',
     INCORRECT_FORMAT_ERROR_MESSAGE),
    ('LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURJVENDQWdtZ0F3SUJBZ0lKQUw1ZGxQc3pYTFlMTUEwR0NTcUdTSWIzRFFFQkN3VUFNQ2N4SlRBakJnTlYKQkFNTUhITmxjblpwYm1jdGMyVnlkbWxqWlM1cmRXSmxMbU5zZFhOMFpYSXdIaGNOTVRnd05qSTJNRGN5TmpJNQpXaGNOTVRrd05qSTJNRGN5TmpJNVdqQW5NU1V3SXdZRFZRUUREQnh6WlhKMmFXNW5MWE5sY25acFkyVXVhM1ZpClpTNWpiSFZ6ZEdWeU1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBNzl0ZE1QS3kKZmpDVkdFbHNMNXRMcDVUeUR0aDhrSFczcUlTU3ZHRVAvVHVzSk9tM1hxbkhoQ1c2aFpSN2tNcWRyd1ZSZUNzVQp6OTVDSnVod0p0TFpSMGVxTVBKbW5EbnhEVmMxb0VVUzE2UTNhOWpqOTBIWTIzZ2h2cXFrcXlYN3cvZzliZnF5CmxuaE16OElYT1JiM0hKVTVWR3V2Q2xMR3ZxNjBOTUxBT3NRZUg3YS9lOU5qdVVWSXdJQTcyenZrQnI0OHcrUWYKMHVGMGVCYUNtOUpobEZLb3d5b3hsN2lWN0FKeHBuS0EyL3M4aHlrMEVoYVhJVE1sUjFmblpnTWF6UEIrV1AvTwpZamJzdmdMNmpNUzR2eTVBbXFXSXJyNkdna2tRdzhOektiRDRSV1U3MWFzenBPQlFVTjlDaE5aVTlzdDkzVjhTCnc4VkFkYWN5WDZXQ2J3SURBUUFCbzFBd1RqQWRCZ05WSFE0RUZnUVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1YKRnlzd0h3WURWUjBqQkJnd0ZvQVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1ZGeXN3REFZRFZSMFRCQVV3QXdFQgovekFOQmdrcWhraUc5dzBCQVFzRkFBT0NBUUVBRjNLSWVrZzl3bndibzhNalhab3Z5ZnIzTXZGT0NiSnIrWkRiCldyajVMSVlSemJkN05BNHZRQkxXeXN1SFVzTVF6UGZUVWJzU3JSTFNEQzdKMGE4c0FaUHYwU1RCL2hpQzRuRDYKVVloWU9uVE95eDFNeUVzQUNUWDJGbWNyQk9wdXliVFlhekdoRXh3QXlEVjFqSmZnanZlMjh0L1RNbVhOeFdJbgpLc0g4S09icTVoTit2bXdnajljakdWbGxSdUdaZFIrZVdoK0ppbEh3dGx9ew9Mk9I1aME1URG1jcUd6WDZPclhQZmZnNHJjCkFXN0FtVlpBVnQzSEF4N1FkZ2xxMkZJMGVCa0FFSEVHb0hvM0xsOGU0Z01rUUIyMDhaZmFvdFFSb2xHYkRLb3EKeENMd3NBd3hXVnlhMHl0aElKMUhhRFJmOWRDSUxOcVZCM29TNThiSEFWMEZGV2o5aVE9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg=',
     INCORRECT_FORMAT_ERROR_MESSAGE),
    ('1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURJVENDQWdtZ0F3SUJBZ0lKQUw1ZGxQc3pYTFlMTUEwR0NTcUdTSWIzRFFFQkN3VUFNQ2N4SlRBakJnTlYKQkFNTUhITmxjblpwYm1jdGMyVnlkbWxqWlM1cmRXSmxMbU5zZFhOMFpYSXdIaGNOTVRnd05qSTJNRGN5TmpJNQpXaGNOTVRrd05qSTJNRGN5TmpJNVdqQW5NU1V3SXdZRFZRUUREQnh6WlhKMmFXNW5MWE5sY25acFkyVXVhM1ZpClpTNWpiSFZ6ZEdWeU1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBNzl0ZE1QS3kKZmpDVkdFbHNMNXRMcDVUeUR0aDhrSFczcUlTU3ZHRVAvVHVzSk9tM1hxbkhoQ1c2aFpSN2tNcWRyd1ZSZUNzVQp6OTVDSnVod0p0TFpSMGVxTVBKbW5EbnhEVmMxb0VVUzE2UTNhOWpqOTBIWTIzZ2h2cXFrcXlYN3cvZzliZnF5CmxuaE16OElYT1JiM0hKVTVWR3V2Q2xMR3ZxNjBOTUxBT3NRZUg3YS9lOU5qdVVWSXdJQTcyenZrQnI0OHcrUWYKMHVGMGVCYUNtOUpobEZLb3d5b3hsN2lWN0FKeHBuS0EyL3M4aHlrMEVoYVhJVE1sUjFmblpnTWF6UEIrV1AvTwpZamJzdmdMNmpNUzR2eTVBbXFXSXJyNkdna2tRdzhOektiRDRSV1U3MWFzenBPQlFVTjlDaE5aVTlzdDkzVjhTCnc4VkFkYWN5WDZXQ2J3SURBUUFCbzFBd1RqQWRCZ05WSFE0RUZnUVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1YKRnlzd0h3WURWUjBqQkJnd0ZvQVVJblc2QWJvbVdmYW05QVROUW1Kc3hVY1ZGeXN3REFZRFZSMFRCQVV3QXdFQgovekFOQmdrcWhraUc5dzBCQVFzRkFBT0NBUUVBRjNLSWVrZzl3bndibzhNalhab3Z5ZnIzTXZGT0NiSnIrWkRiCldyajVMSVlSemJkN05BNHZRQkxXeXN1SFVzTVF6UGZUVWJzU3JSTFNEQzdKMGE4c0FaUHYwU1RCL2hpQzRuRDYKVVloWU9uVE95eDFNeUVzQUNUWDJGbWNyQk9wdXliVFlhekdoRXh3QXlEVjFqSmZnanZlMjh0L1RNbVhOeFdJbgpLc0g4S09icTVoTit2bXdnajljakdWbGxSdUdaZFIrZVdoK0ppbEh3dGxaME1URG1jcUd6WDZPclhQZmZnNHJjCkFXN0FtVlpBVnQzSEF4N1FkZ2xxMkZJMGVCa0FFSEVHb0hvM0xsOGU0Z01rUUIyMDhaZmFvdFFSb2xHYkRLb3EKeENMd3NBd3hXVnlhMHl0aElKMUhhRFJmOWRDSUxOcVZCM29TNThiSEFWMEZGV2o5aVE9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg',
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
     """{"title": "'name' parameter required"}"""),
    ({'name': TENANT_NAME, 'cert': CERT, 'quota': QUOTA},
     """{"title": "'scope' parameter required"}"""),
    ({'name': TENANT_NAME, 'scope': SCOPE_NAME, 'quota': QUOTA},
     """{"title": "'cert' parameter required"}"""),
    ({'name': TENANT_NAME, 'cert': CERT, 'scope': SCOPE_NAME},
     """{"title": "'quota' parameter required"}"""),
]

QUOTA_WRONG_VALUES = [
    ({'requests.cpu': '-1',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     """{"title": "Invalid value -1 of requests.cpu field: must be integer greater than or equal to 0"}"""),

    ({'requests.cpu': '1-',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     """{"title": "Invalid value 1- of requests.cpu field: must be integer greater than or equal to 0"}"""),

    ({'requests.cpu': 'a',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     """{"title": "Invalid value a of requests.cpu field: must be integer greater than or equal to 0"}"""),

    ({'requests.cpu': '1a',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     """{"title": "Invalid value 1a of requests.cpu field: must be integer greater than or equal to 0"}"""),

    ({'requests.cpu': '1',
      'requests.memory': '1Gi',
      'limits.cpu': '-1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     """{"title": "Invalid value -1 of limits.cpu field: must be integer greater than or equal to 0"}"""),

    ({'requests.cpu': '1',
      'requests.memory': '1Gi',
      'limits.cpu': '1a',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     """{"title": "Invalid value 1a of limits.cpu field: must be integer greater than or equal to 0"}"""),

    ({'requests.cpu': '1',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '-1'},
     """{"title": "Invalid value -1 of maxEndpoints field: must be integer greater than or equal to 0"}"""),

    ({'requests.cpu': '1',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': 'a'},
     """{"title": "Invalid value a of maxEndpoints field: must be integer greater than or equal to 0"}"""),

    ({'requests.cpu': '1',
      'requests.memory': '-1Gi',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     """{"title": "Invalid value -1Gi of requests.memory field. Please provide value that matches Kubernetes convention. Some example values: '1Gi', '200Mi', '300m'"}"""),

    ({'requests.cpu': '1',
      'requests.memory': '1Gi-',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     """{"title": "Invalid value 1Gi- of requests.memory field. Please provide value that matches Kubernetes convention. Some example values: '1Gi', '200Mi', '300m'"}"""),

    ({'requests.cpu': '1',
      'requests.memory': '1Ga',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     """{"title": "Invalid value 1Ga of requests.memory field. Please provide value that matches Kubernetes convention. Some example values: '1Gi', '200Mi', '300m'"}"""),

    ({'requests.cpu': '1',
      'requests.memory': 'a1',
      'limits.cpu': '1',
      'limits.memory': '1Gi',
      'maxEndpoints': '1'},
     """{"title": "Invalid value a1 of requests.memory field. Please provide value that matches Kubernetes convention. Some example values: '1Gi', '200Mi', '300m'"}"""),

    ({'requests.cpu': '1',
      'requests.memory': '1Gi',
      'limits.cpu': '1',
      'limits.memory': '1-Gi',
      'maxEndpoints': '1'},
     """{"title": "Invalid value 1-Gi of limits.memory field. Please provide value that matches Kubernetes convention. Some example values: '1Gi', '200Mi', '300m'"}"""),
]

PORTABLE_SECRETS_PATHS = ['default/minio-access-info', 'default/tls-secret']

configuration = config.load_kube_config()
api_instance = client.CoreV1Api(client.ApiClient(configuration))

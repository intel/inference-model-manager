# inferno-platform
[![CircleCI](https://circleci.com/gh/NervanaSystems/inferno-platform.svg?style=svg&circle-token=677ac34c125509e550220a080f4f8f68dfb8729c)](https://circleci.com/gh/NervanaSystems/inferno-platform)

source code, deployment automation and tests for inference platform POC made for Blizzard

## management
### management-api
* `export MANAGEMENT_HOSTNAME=0.0.0.0`
* `export MANAGEMENT_PORT=[port]`
* `export MINIO_ENDPOINT=[minio_endpoint]`

* `export IMAGE=<management-api image name>` (default: management-api)
* `export TAG=<management-api tag>` (default: latest)


Run these commands from `management` catalog in order to build docker image or run management api with docker
* `make build`
* `make run`

If you run Docker container with API locally, you need to copy your $HOME/.kube/config with credentials to particular cluster to management folder.

#### local development
* create virtualenv (`virtualenv .venv`)
* activate virtualenv (`. .venv/bin/activate`)
* install dependencies (`make install`)
* run minio server (`minio server /data`) (OPTIONAL: '--address: ":minio-port")
* get minio accessKey and secretKey from ~/.minio/config.json (that's default location for minio config file, updated after minio server run), you can use
helpers/get_minio_credentials.sh)
  * get_minio_credentials.sh gets accessKey and secretKey from `~/.minio/config.json` and exports these to `MINIO_ACCESS_KEY_ID` and
  `MINIO_SECRET_ACCESS_KEY`:
    ```
    . helpers/get_minio_credentials.sh
    ```
* run (`management-api`)

#### local development + testing on external environment (i.e. gcloud)
* *can be done locally* 
	* `make build` - build docker image
	* `make tag` - tag image
	* `make push` - push image to gcr
* *on environment, i.e. on gcloud)*
	* goto helm-deployment catalog 
	* remove existing k8s resources and helm release (i.e. you can use script 
	`delete_all.sh` from helpers catalog)
	* *optional* change values (i.e. management-api image)
	(`helm-deployment/charts/management-api-subchart/values.yaml`)
	* `helm install .`
	
### Examples

#### Tenants
Create tenant:
```
curl -X POST "http://<management_api_address>:5000/tenants" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"cert\": \"<cert_encoded_with_base64>\", \"scope\": <string>, \"name\": <string>, \"quota\": <dict>}"
```
Delete tenant:
```
curl -X DELETE "http://<management_api_address>:5000/tenants" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" -d "{\"name\": <string>}"
```

Cert field value is used in kubernetes secret. Because of that, cert shall be provided in Base64 encoded format.
* example with valid certificate:
```
curl -X POST "http://<management_api_address>:5000/tenants" -H "accept: application/json" -H "Authorization: '<jwt_token>'" \
-H "Content-Type: application/json" -d "{\"name\": \"tenant-name\", \"cert\":\"LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tDQpNSUlGSVRDQ0F3bWdBd0lCQWdJSkFQMUpTL283ZEt3WE1BMEdDU3FHU0liM0RRRUJDd1VBTUNjeEpUQWpCZ05WDQpCQU1NSEhObGNuWnBibWN0YzJWeWRtbGpaUzVyZFdKbExtTnNkWE4wWlhJd0hoY05NVGd3T0RBeE1EZ3dPVE00DQpXaGNOTVRrd09EQXhNRGd3T1RNNFdqQW5NU1V3SXdZRFZRUUREQnh6WlhKMmFXNW5MWE5sY25acFkyVXVhM1ZpDQpaUzVqYkhWemRHVnlNSUlDSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQWc4QU1JSUNDZ0tDQWdFQXV5R24vSTZ1DQp2dzNQcXdaN0pPVVRNdlNiL3ZiajRaNE5hTFdTb2J5dlFMT2JHNndrVzdkOW11c1M3clRSRGN0QUVqaVBTVktXDQp4eDhrcklXSkZmR05tZlVjQnNjbWwzMVpVeThiVUJCMVdIT2ZoM2dZT1h3SXUvZDFHR0gyaWQ3ZHhScHJJY1hkDQphSkM3TjRFQjltNEVkaWFSbjNGRGRsNm5FcDlUU1pSVy8xazJyTmpyRlVpUUh4NU5PRk96NEVVRDJ4YWh6cVB5DQpPUnhHV3lHdVRmQmhGb21NWWRGT3pUS09sVXZuVDc3UDh4WEhEbFFPZWNCN0RvWkdhTjBsUnRSOWpUREJFRmVMDQovYlgrYWI2YW5kTFk3OEx3N1NQYjZsQWF0QmdRWWZBVzV0ZlVVNGVJbGNGSjE4SFJ5b2I3SiswUFh1YkZlUVFlDQp1enBsMHg4WTVCdndKazVYV1RLakhpNDFMNkJ5amF6K0c2QzB6VzFCM2pOY0tWYXZuYjBsSlhTejkzcUNyeUMrDQpsQVU5WFFiMmhXcTBib3o0ZGhBbm9mWVV2Vi9sNGJnekV1U2tGamp2ZlRIRGpXdUYwWUtwQ0ZWdlBQVUh2UE91DQpSSmtkNWxMNDFObTNMZFVHbUdEcEZhQ29mSWp3NjI4bHFEZ1dJbUJ4UGtLRURLUnRnWmtkcElKRlJSdVNYcll4DQpIWThqNkhvT0ZqR2dSSDZ3TTFHdmJyb3h2bk0vZ01xWHhrOXArMXZZQWVPdmtHVlBFNS9pMWVDbDM5bjdqTExzDQpTcjNFQmhTTFFxb2srMGMvVnE3cVFSck4vZktWd2pEOW5FcGJyQmR5YStWelozTVJ2QkE5WDBHbjVnb3BhdjJxDQpVL0p1ajg1RGNaUG5iVGI4a0ZlVzFWOGNkT1ZwengzV0Ixa0NBd0VBQWFOUU1FNHdIUVlEVlIwT0JCWUVGTkdXDQpjSURBdFhyTFFMSHpRb0hpa2MvVEpBeXpNQjhHQTFVZEl3UVlNQmFBRk5HV2NJREF0WHJMUUxIelFvSGlrYy9UDQpKQXl6TUF3R0ExVWRFd1FGTUFNQkFmOHdEUVlKS29aSWh2Y05BUUVMQlFBRGdnSUJBTEpoYm1hMXNYSFdnaWNmDQpjTmNEZ0Z5OEcyV2N4dk1ja2s2MkE3ZGw1ODhVUW1VYnBHbEpicVJ5Q0Evak1lNERhOEFFSHUrWUxCRkVjRURVDQo5V2liS3AyQ0xkVFlwYnBDbzRxeXhBallRZ2lCdWlJNms3aWJuMG9DSVBhTFZRelcxKzlac21SVEFtSTg1cWpqDQpscTQwS3UvZEgxeXdua2RKemNBNDE1V3h1MFU5a3hyVktZUzRheG1pRENRdlI1bmxJeDdGcHdlNVEybEgrZllMDQpJYVIxMVNPcGVpMFZlcEQvb0tQcHp0Mk05dmZ0OW9ReEVTZ3NLaGd2RmdmTHhJbjlrMXRZRDkwdFBkb2w5dzBEDQoxblFqbkZZc1c1VG9LOGJ3UHc2WnJWY05VY0Q3ZWhGYnJyTDNOMUZ5TWFIWHIwWjd4d2lpbHZSWjdQOEM0ZjE5DQoxZkR5ZDZvS29XcU5teDlBQmlJcEdjeFd1NE9pY2swQnkrcmhVQks3My80ZXFpZS9GeDdFd0ZNbEdtRHFLdlNmDQpIWjJua1YyOFpDWHM4WHNzNVZvRFRkSzR6alRjVXNSdmdNSG5XZUVOT2RTaXNXMm9tcGFYc2xHdjRER3U0SXplDQorYk11cnhQOUIwRXp6T0hpNlVOYmhvUVBGYy9DNkYxQ0hsZ2Qra3BPaHlPdno2dmxNNEtsMmp5YTRDWWVvWWF3DQpmbEZ1UE1CMElKMlZlZ1puWFVyd0VRYXBrM0JFODF1NTRaNzR3Q3greE5LbFdhTWZhN2Vmb1I0K0J2Tkw0VkZ4DQpxTHNMSVJrM202aUpDcmMvR3F4eVJOdTAyZDJyQXBFMEpGNklITmFtY292UWdKUmg3OHVvZ3Fyekc1SXlhR2kwDQpnVHZoT3FpSkthM1pGV2ErNnA0TTRzNE03TndtDQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tDQo=\", \
\"scope\": \"test\", \"quota\": {\"requests.cpu\": \"1\", \"requests.memory\": \"1Gi\", \"limits.cpu\": \"2\", \"limits.memory\": \"2Gi\", \"maxEndpoints\": 15}}"
```

#### Endpoints
Create endpoint
```
curl -X POST "http://<management_api_address>:5000/tenants/<namespace>/endpoints" -H "accept: 
application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"modelName\": <string>, \"modelVersion\": <int>, \"endpointName\": <string>, \"subjectName\": <string>
\"resources\": {<dict>}}"
```
```resources``` field is optional.

Scale endpoint
```
curl -X PATCH "http://<management_api_address>:5000/tenants/<namespace>/endpoints/<endpoint-name>/scaling" \
-H "accept: application/json" -H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"replicas\": <int>}"
```

Update endpoint
```
curl -X PATCH "http://<management_api_address>:5000/tenants/<namespace>/endpoints/<endpoint-name>/updating" \
-H "accept: application/json" -H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"modelName\": <string>, \"modelVersion\": <int>}"
```

View endpoint
```
curl -X GET "http://<management_api_address>:5000/tenants/<namespace>/endpoints/<endpoint-name>/viewing" \
-H "accept: application/json" -H "Authorization: <jwt_token>" -H "Content-Type: application/json"

```

List endpoints
```
curl -X GET "http://<management_api_address>:5000/tenants/<namespace>/endpoints" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json"
```
#### Models

Delete model
```
curl -X DELETE "<management_api_address>:5000/tenants/<namespace>/models" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"modelName\": <string>, \"modelVersion\": <int>}"

```

#### Inference endpoints
E2E test using resnet model, scripts: https://github.com/NervanaSystems/inferno-platform/tree/demo-helpers/helpers/demo
- create new tenant
- copy existing resnet model into newly created bucket (if you're using scripts from 
demo-helpers, please remember about mc configuration i.e. `mc config host add local http://127.0
.0.1:9000 [access_key] [secret_key]`)
- create new endpoint - in response you'll find IP address and opts
- use endpoint_test.py to test whether your inference endpoint works or not
  - check if paths to certs in endpoint_test.py are correct (you can use certs from 
  helm-deployment catalog)
  - install all needed dependencies (you can use requirements.txt from tests catalog)
  - `export OPTS = <endpoint_domain> `i.e. resnet.serving-service.com
  - `export HOST = <ingress_ip>:<port>` i.e. 127.0.0.1:443
  - `export MODEL = <model_name> `(use modelName provided in create_endpoint request)
  - run endpoint_test.py

## scripts
### authenticate
A special script for authentication has been created, it is available under the path:
```
    cli-scripts/webbrowser_authenticate.py
```
It runs the appropriate page for authentication in the browser, then after the correct login it saves the token and refresh token to the file.
By default this is the path "~ / .inferno".
This path can be changed by setting the "INFERNO_CONFIG" environment variable.
Command to run the script:

```
    python cli-scripts/webbrowser_authenticate.py --address <ip_to_management_api>
```
It works with both python versions.
By default, management_api runs on port 5000 and this port is used in this script. To change this, add another flag when you start the script:
```
    python cli-scripts/webbrowser_authenticate.py --address <management_api ip> --port <management_api port>
```


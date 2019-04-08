# Management API

Management API component provides a convenience layer for controlling CRD records and handling AI models in Minio storage.
With that users and platform admin can control all aspects of Inference Endpoints functionality without direct access
to Kubernetes API. 

Authorization of the models management functions is implemented based on user token permissions in kubernetes namespace 
associated with the Minio bucket.
 
All the kubernetes operations are executed by Management API component using the user token so the authorization 
is configured in Kubernetes using appropriate user roles and role bindings. 

The roles and permissions are created automatically by Management API during tenant creation. 


## Docker image building

```
make docker_build
```
While the docker image is built it should be pushed to a docker registry accessible by the K8S cluster.

## Deployment in Kubernetes cluster

Refer to the [helm chart](../helm-deployment/management-api-subchart) documentation. 


## API documentation

### Tenants
Tenants are managed by Platform Admin. It is possible to take actions as follow:
* create tenant,
* delete tenant,
* list tenants.

#### Create tenant

Call a POST operation on `https://<management-api-address>/tenants`:
```
curl -X POST "https://<management_api_address>/tenants" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"name\": <string>, \"cert\": <cert_encoded_with_base64>, \"scope\": <string>, \"quota\": {}}"
```

When an operation ends with success, it returns a statement (example for a tenant with a name `test`):

```{"status": "CREATED", "data": {"name": "test"}}```

#### Quota configuration for tenant

Call a POST operation on `https://<management-api-address>/tenants` with quota defined:
```
curl -X POST https://<management-api-address>/tenants -H “accept: application/json” \
H “Authorization: <id-token>” H “Content-Type: application/json” d {\”name\”: <string>, \ 
\”cert\”: <cert_encoded_with_base64>\”, \”scope\”: <string>, \
\”quota\”: {\”maxEndpoints\”: <int>, \”requests.cpu\”: <string>, \”limits.cpu\”: <string>, \ 
\”requests.memory\”: <string>, \”limits.memory\”: <string>}}
```

Quota parameter is required, but there is an option to pass an empty dictionary instead of resource specification
(see Create tenant).

#### List tenants

Call a GET operation on `https://<management-api-address>/tenants`:
```
curl -X GET "https://<management_api_address>/tenants" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json"
```

When an operation ends with success, it returns a statement (example for a tenant with a name `test`):
 
```{"status": "OK", "data": {"tenants": ["test"]}}```


#### Delete tenant

Call a DELETE operation on `https://<management-api-address>/tenants`:
```
curl -X DELETE "https://<management_api_address>/tenants" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" -d "{\"name\": <string>}"
```

When an operation ends with success, it returns a statement (example for a tenant with a name `test`):
 
```{"status": "DELETED", "data": {"name": "test"}```

##
### Models 
Models are pretrained deep learning models able to be served via Tensoflow Serving.

#### Upload model
To upload model use `scripts/model_upload_cli.py`.  
Run help to get information about usage:
```
python model_upload_cli.py -h
```

#### List models
Call a GET operation on `https://<management-api-address>/tenants/<tenant-name>/models`:

```
curl -X GET "https://<management_api_address>/tenants/<tenant-name>/models" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" }"
```

When an operation ends with success, it returns a statement (example for a tenant `test`):
```
{"status": "OK", "data": {"models": [{"path": "resnet/1/saved_model.pb",
"name": "resnet", "version": "1", "size": 102619858}, {"path": "resnet/2/saved_model.pb",
"name": "resnet", "version": "2", "size": 102619858}]}}
```

#### Delete model
Call a DELETE operation on `https://<management-api-address>/tenants/<tenant-name>/models`:
```
curl -X DELETE "https://<management_api_address>/tenants/<tenant-name>/models" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"modelName\": <string>, \"modelVersion\": <int>}"
```
When an operation ends with success, it returns a statement (example for a model `resnet` in version 1):
```
{"status": "DELETED", "data": {"model_path": "resnet/1/"}}
```

##
### Endpoints
Endpoints are managed by Platform Users. It is possible to take actions as follow:
* create endpoint
* view endpoint
* update endpoint
* scale endpoint
* delete endpoint
* list endpoints

#### Model version policy
In order to specify particular model versions to be served, provide `modelVersionPolicy` parameter
 while creating or updating endpoint. `modelVersionPolicy` parameter is a string limited to:
 * `{ latest {} }` - only latest version of the model will be served,
 * `{ all {} }` - all available versions of the model will be served,
 * `{ specific { versions: 1 versions: 2 ... }` - specified versions of the model will be
  served 
  
If `modelVersionPolicy` parameter was not provided during endpoint creation, default 
  value is 
`{latest {}}`.

#### Create endpoint
Call a POST operation on `https://<management-api-address>/tenants/<tenant-name>/endpoints`:
```
curl -X POST "https://<management_api_address>/tenants/<tenant-name>/endpoints" -H "accept: 
application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"endpointName\": <string>, \"modelName\": <string>, \"modelVersionPolicy\": <string>, 
\"servingName\": <string>,
 \"subjectName\": <string>, \"resources\": <dict>}"
```

When an operation ends with success, it returns a statement (example for an endpoint with a name 
`endpoint` in a `test` tenant with a `test-domain.com` domain):
```
{"status": "CREATED", "data": {"url": "endpoint-test.test-domain.com:443", "warning": ""}}
```

`warning` field is responsible for passing warning information about the non-existence of the 
model to which endpoint is pointing. In this case, response from platform will be:
```
{"status": "CREATED", "data": {"url": "endpoint-test.test-domain.com:443", 
"warning": "resnet model is not available on the platform"}}
```

#### List endpoints
Call a GET operation on `https://<management-api-address>/tenants/<tenant-name>/endpoints`:
```
curl -X GET "https://<management_api_address>/tenants/<tenant-name>/endpoints" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json"
```

When an operation ends with success, it returns a statement (example for endpoins `endpoint1` and 
`endpoint2` in a `test` tenant with a `test-domain` domain):
```
{"status": "OK", "data": {"endpoints": 
[{'name': 'endpoint1', 'url': 'endpoint1-test.test-domain.com:443', 'status': 'available'}, 
{'name': 'endpoint2', 'url': 'endpoint2-test.test-domain.com:443', 'status': available'}]}}
```

#### Delete endpoint
Call a DELETE operation on `https://<management-api-address>/tenants/<tenant-name>/endpoints`:
```
curl -X DELETE "https://<management_api_address>/tenants/<tenant-name>/endpoints" \
-H "accept: application/json" -H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"endpointName\": <string>}"
``` 

When an operation ends with success, it returns a statement (example for an `endpoint` in tenant `test`):
```
{"status": "DELETED", "data": {"url": "endpoint-test.test-domain.com:443"}}
```

#### View endpoint
Call a GET operation on 
`https://<management-api-address>/tenants/<tenant-name>/endpoints/<endpoint-name>`:
```
curl -X GET "https://<management_api_address>/tenants/<tenant-name>/endpoints/<endpoint-name>" \
-H "accept: application/json" -H "Authorization: <jwt_token>" -H "Content-Type: application/json"
```

When an operation ends with success, it returns a statement (example for an endpoint with a name 
`endpoint` from `test` tenant):
```
{"status": "OK", "data": {"endpoint status": {"running pods": 1, "pending pods": 0, "failed pods": 0}, 
"endpoint url": "endpoint-test.test-domain.com:443", "subject name": "client", 
"resources": {"requests": {"cpu": "1", "memory": "1Gi"}, "limits": {"cpu": "2", "memory": "2Gi"}}, 
"replicas": {"available": 1, "unavailable": None}}}
```

#### Update endpoint
Call a PATCH operation on `https://<management-api-address>/tenants/<tenant-name>/endpoints/<endpoint-name>:`

```
curl -X PATCH "https://<management_api_address>/tenants/<tenant-name>/endpoints/<endpoint-name>" \
-H "accept: application/json" -H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"modelName\": <string>, \"modelVersionPolicy\": <string>, \"resources\": <dict>, \"subjectName\": <string>}"
```
Parameters: `modelName`, `modelVersionPolicy`, `resources`, `subjectName` are optional.

When an operation ends with success, it returns a statement (example for an endpoint with a name 
`endpoint` from `test` with modelName and modelVersionPolicy updated):
```
{"status": "PATCHED", "data": {"url": "endpoint-test.example-domain.com:443", 
"values": {"modelName": "new-model", "modelVersionPolicy": "{latest {}}"}}}
```

#### Scale endpoint

Call a PATCH operation on `https://<management-api-address>/tenants/<tenant-name>/endpoints/<endpoint-name>/replicas`:

```
curl -X PATCH "https://<management_api_address>/tenants/<tenant-name>/endpoints/<endpoint-name>/replicas" \
-H "accept: application/json" -H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"replicas\": <int>}"
```
When an operation ends with success, it returns a statement (example for an endpoint with a name 
`endpoint` from `test`):
```
{"status": "PATCHED", "data": {"url": "endpoint-test.example-domain.com:443", "values": {"replicas": 2}}}
```

### Servings

#### List servings
Call a GET operation on `https://<management-api-address>/servings`:
```
curl -X GET "https://<management_api_address>/servings" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json"
```

When an operation ends with success, it returns a statement (example for a two default serving templates):
```
{"status": "OK", "data": ["ovms", "tf-serving"]}
```

#### Get serving
Call a GET operation on `https://<management-api-address>/servings/<serving-name>`:

```
curl -X GET "https://<management_api_address>/servings/<serving_name>" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json"
```

When an operation ends with success, it returns a statement (example for a `tf-serving`):
```
{"status": "OK", "data": {"configMap.tmpl": <yaml template>, "deployment.tmpl": <yaml template>,
"ingress.tmpl": <yaml template>, "service.tmpl": <yaml template>}}
```

## Script for API calls

You can refer to `imm` example CLI employing all API endpoints on [scripts](../scripts/)
